import json
import random
import string
import time
import pytz
import requests
from datetime import datetime
from flask import request
from app.settings import CODE_API, HTTP_STATUS_MESSAGE

# ============================================  QUERY  ============================================
class QueryBuilder:
    def __init__(self, table, **kwargs):
        self.query = ''
        self.query_total = ''
        self.table = table
        self.customer_id = kwargs.get('customer_id')
        self.orfer_by = kwargs.get('order_by')

    def get_sql(self, is_debug=False):
        _query = self.query
        if is_debug:
            print(f'\033[1m\033[96m self.query >>>>>>>>> {self.query} \33[0m', flush=True)
        self.query = ""
        return _query
        
    def get_sql_total(self):
        _query_total = self.query_total
        self.query_total = ""
        return _query_total
    
    @staticmethod
    def convert_field_lookup(field_lookup, value):
        field_lookup_explore = field_lookup.rsplit('__', 1)
        str_value = "'" + value + "'" if isinstance(value, str) else value
        if len(field_lookup_explore) == 1:
            return field_lookup + ' = ' + str(str_value) if value is not None else field_lookup + ' IS NULL '
        
        field = field_lookup_explore[0]
        operator = field_lookup_explore[1].lower()
        if operator == "is_null":
            return f"{field} IS NULL"
        if operator == "not null":
            return f"{field} IS NOT NULL"
        if operator == "eq":
            return f"{field} = {str_value}"
        if operator == "not_equal":
            return f"{field} <> {str_value}"
        if operator == "gt":
            return f"{field} > {str_value}"
        if operator == "lt":
            return f"{field} < {str_value}"
        if operator == "gte":
            return f"{field} >= {str_value}"
        if operator == "lte":
            return f"{field} <= {str_value}"
        if operator == "contains":
            return f"{field} LIKE '%{value}'"
        if operator == "cast_text_contains":
            return f"CAST({field} as TEXT) LIKE '%{value}%'"
        if operator == "icontains":
            return f"{field} ILIKE '%{value}%'"
        if operator == "startswith":
            return f"{field} LIKE '{value}%'"
        if operator == "endswith":
            return f"{field} LIKE '%{value}'"
        if operator == "in" or operator == "not_in":
            if operator == "not_in":
                operator = "not in"
            result = '{}'
            if None in value:
                if len(value) > 1:
                    value.remove(None)
                    result = '({} OR %s IS NULL)' % (field)
                else:
                    return field + ' IS NULL'
            return result.format(field + " " + operator.upper() + " " + str(value).replace('[', '(').replace(']', ')'))
        
    def select(self, columns=[], alias='', from_tb=''):
        self.query = ''
        self.query = "SELECT " + ", ".join(columns) if columns else "SELECT *"
        if not from_tb:
            from_tb = self.table
        self.query += f"FROM {from_tb}"
        if alias:
            self.query += f" {alias}"
    
    def join(self, join_table='', condition=[], type='INNER', join_table_alias=''):
        if join_table_alias:
            join_table += f' AS {join_table_alias}'
        if join_table and condition:
            condition_list_str = []
            for item in condition:
                if isinstance(item[1], str) and "'" in item[1]:
                    item[1].replace("'", "''") # Simple escape
                if '__' not in item[0]:
                    condition_list_str.append(item[0] + " = " + item[1])
                else:
                    where_string = QueryBuilder.convert_field_lookup(item[0], item[1])
                    if where_string:
                        condition_list_str.append(where_string)
            self.query += " " + type.upper() + " JOIN" + join_table + " ON " + (' AND '.join(condition_list_str))

    def where(self, condition=None, exclude=['keyword'], active=None, table_active=None):
        """Where query builder
        Args:
            condition (dict, optional): condition. Defaults to None.
            exclude (array, optional): exclude condition. Defaults to ['keyword'].
            active (any, optional): check record active. Defaults to True. Value must be: 'all', True, False
        """ 
        self.query += " WHERE"
        if not condition or not isinstance(condition, dict):
            self.query += " TRUE"
        if not table_active:
            table_active = self.table
        if active != 'all' and active is not None and isinstance(active, bool):
            condition[f'{table_active}.active'] = active
        for key in condition.keys():
            if key in exclude:
                continue
            if key == 'sql_string':
                self.query += f" AND ({condition[key]})"
                continue
            if isinstance(condition[key], str) and "'" in condition[key]:
                condition[key] = condition[key].replace("'", "''")
            field = f'{self.table}.{key}' if '.' not in key and self.table else key
            where_string = QueryBuilder.convert_field_lookup(field, condition[key])
            if where_string:
                self.query += f" AND {where_string}"
        self.query = self.query.replace("WHERE AND", "WHERE")

    def like(self, fields=['name'], keyword='', condition=''):
        if not keyword:
            return
        if not (condition and isinstance(condition, str) and condition.upper() in ['LIKE', 'ILIKE']):
            condition = 'ILIKE'
        keyword = keyword.replace(' ', '')
        if isinstance(keyword, str) and "'" in keyword:
            keyword.replace("'", "''")
        list_query_str = []
        for item in fields:
            list_query_str.append(f"lower(replace({item}, ' ', '')) {condition} lower('%{keyword}%')")
        if len(list_query_str):
            self.query += " AND (" + ' OR '.join(list_query_str) + ")"
        self.query = self.query.replace("WHERE AND", "WHERE")

    def extend(self, options={}, **kwargs):
        group_by = options.get('group_by')
        order_by = options.get('order_by') or self.order_by
        limit = options.get('limit')
        offset = options.get('offset')
        if group_by:
            self.query += f' GROUP BY {group_by}'
        if order_by:
            order_by_convert = []
            if not isinstance(order_by, list) or isinstance(order_by, tuple):
                order_by = [order_by]
            for item_order_by in order_by:
                # Nối tên table vào ORDER BY, nhưng phải trừ các TH đã có "table." hoặc "()".
                # VD: random()
                if '.' not in item_order_by and '()' not in item_order_by and 'TO_CHAR' not in item_order_by:
                    item_order_by = f'{self.table}.{item_order_by}'
                order_by_convert.append(item_order_by)
            self.query += ' ORDER BY ' + ', '.join(order_by_convert)
        if limit:
            self.query += f' LIMIT {limit}'
        if offset:
            self.query += f' OFFSET {offset}'

    def insert(self, params: dict, has_create_date=False, has_create_id=False, multi_insert=False):
        params = clean_dict(params)
        if not params:
            return
        if not multi_insert:
            if has_create_date:
                params['create_date'] = str(get_datetime_now())
            if has_create_id:
                params['create_id'] = self.customer_id
            columns = str(tuple(params.keys())).replace("'", "")
            # Escape string
            for key in params:
                if isinstance(params[key], str) and "'" in params[key]:
                    params[key] = params[key].replace("'", "''")
                params[key] = "'%s'" % params[key]
            value_str = ", ".join(params.values())
            self.query = "INSERT INTO {} {} VALUES ({})".format(self.table, columns, value_str)
        else:
            first_key = list(params.keys())[0]
            len_items = len(params[first_key])
            if has_create_date:
                params['create_date'] = [str(get_datetime_now())] * len_items
            columns = str(tuple(params.keys())).replace("'", "")
            values = tuple(zip(*params.values()))
            self.query = "INSERT INTO {} {} VALUES {}".format(self.table, columns, str(values).replace("((", "(").replace("))", ")")).replace('),)', ')')

    def update(self, params, has_update_info=False, clean_params=True):
        if has_update_info:
            params['update_id'] = self.customer_id
            params['update_date'] = str(get_datetime_now())
        self.query = f"UPDATE {self.table} SET "
        list_data_str = []
        for key, val in params.items():
            if not key:
                continue
            k = key.rsplit('__', 1)
            field = k[0]
            f_type = k[1] if len(k) > 1 else None
            if val == None:
                list_data_str.append(field + " = NULL")
                continue
            if f_type == 'json':
                val = str(val).replace("'", '"')
                list_data_str.append(f"{field} = '{val}'::json")
                continue
            if isinstance(val, list):
                list_data_str.append(f"{field} = {json.dumps(val)}")
                continue
            list_data_str.append(field + " = " + ("'" + str(val) + "'" if isinstance(val, str) else str(val)))
        self.query += ', '.join(list_data_str)

    def delete(self):
        self.query = "DELETE FROM {}".format(self.table)
    
    def convert_column(self, columns):
        columns = columns.copy()
        if not bool(columns):
            return [f'{self.table}.*']
        res = []
        for item in columns:
            if '(' in item:
                res.append(item)
                continue
            if '.' not in item:
                item = f'{self.table}.{item}'
            res.append(item)
        return res
    
class ErrorToClient(Exception):
    def __init__(self, *args, **kwargs):
        if kwargs.get('http_status'):
            self.http_status = kwargs['http_status']
            if kwargs.get('message'):
                self.message = kwargs['message']
        super().__init__(*args)
        

# ============================================  OTHER FUNCTIONS  ============================================ #

def uuid():
    return str(int(time.time())) + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(12))

def log_error(exception, name=None, exec_info=False, customer_id=''):
    import logging
    logger = logging.getLogger()
    customer_info = f'- (id: {customer_id})' if customer_id else ''
    logger.error(f'\033[1m \033[91m [Error in `{name}` {customer_info}] {exception} \033[0m', exc_info=exec_info)

def get_response(http_status=200, status_code=None, data=None, message=None, is_keep_alive=True, extra_params={}):
    res = {}
    if status_code:
        res['code'] = CODE_API.get(status_code)
    if http_status in HTTP_STATUS_MESSAGE:
        res['code'] = HTTP_STATUS_MESSAGE[http_status]['api_code']
        res['message'] = HTTP_STATUS_MESSAGE[http_status]['message']
    if data is not None:
        res['data'] = data
    if message:
        res['message'] = message
    if extra_params:
        res.update(extra_params)
    if is_keep_alive:
        return res, http_status, {'Connection': 'keep-alive'}
    return res, http_status

def clean_dict(data: dict, is_remove_empty_str=False):
    res = {}
    for key, value in data.items():
        if value in (None, []) or (is_remove_empty_str and value == ''):
            continue
        res[key] = value
    return res

def translate_bad_request_message(message=None):
    if 'Missing required parameter in the post body' in message:
        message = message.replace('Missing required parameter in the post body', 'Thiếu trường dữ liệu bắt buộc')
    if 'is not a valid choice' in message:
        message = message.replace('is not a valid choice', 'không phải là một lựa chọn hợp lệ')
    if 'invalid literal for int() with base 10' in message:
        message = message.replace('invalid literal for int() with base 10', 'Dữ liệu không phải số nguyên')
    if 'could not convert string to float' in message:
        message = message.replace('could not convert string to float', 'Không định dạng được số thực')
    return message

def get_dict_value_by_id(data, id):
    if isinstance(id, list):
        return [data.get(i) for i in id]
    return data.get(id)

def get_request_headers():
    return request.headers

def list_to_dict(data: list, key: str = 'id', value: str = None):
    if not (bool(data) and isinstance(data, list)):
        return {}
    res = {}
    for item in data:
        if key not in item:
            continue
        res[item[key]] = item[value] if value in item else item
    return res

# Convert list to json
def convert_to_json(data, task=None):
    res = {}
    if task == 'key_value':
        if not isinstance(data, list):
            return res
        for item in data:
            list_key = list(item.keys())
            if len(list_key) == 2:
                value = item[list_key[1]]
                if not isinstance(value, int) or not isinstance(value, str):
                    value = str(value)
                    res.update({item[list_key[0]]: value})
            else:
                key = item[list_key[0]]
                res[key] = {}
                for idx in range(1, len(list_key)):
                    value = item[list_key[idx]]
                    if not isinstance(value, int) or not isinstance(value, str):
                        value = str(value)
                    res[key].update({list_key[idx]: item[list_key[idx]]})
    return res

def random_string():
    letters = string.ascii_lowercase
    random_str = ''.join(random.choice(letters) for i in range(8))
    return get_datetime_now().strftime("%Y%m%d%H%M%S") + random_str

def get_datetime_now():
    return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).replace(tzinfo=None)

def get_version():
    from flask import request
    path = request.path.split('/')
    return path[1]



