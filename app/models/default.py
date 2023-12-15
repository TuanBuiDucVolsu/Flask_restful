from app.helpers.functions import QueryBuilder, uuid
from app.connect_database import ConnectModel

class DefaultModel():
    cache_fields = ('id', 'name')
    def __init__(self, table, **kwargs):
        self.table = table
        self.db_alias = kwargs.get('db_alias', 'default')
        self.customer_id = kwargs.get('customer_id')
        self.active = kwargs.get('active')
        self.order_by = kwargs.get('order_by')
        self.search_fields = kwargs.get('search_fields', ('name',))
        self.has_create_date = kwargs.get('has_create_date', False)
        self.has_create_id = kwargs.get('has_create_id', False)
        self.has_update_info = kwargs.get('has_update_info', False)
        self.qb = QueryBuilder(self.table, customer_id=self.customer_id, order_by=self.order_by)
        self.model_connect = ConnectModel(self.db_alias)

    def get_cache(self, condition={}, **kwargs):
        return self.get_raw_data(columns=list(self.cache_fields), condition=condition, is_list=True, **kwargs)
    
    def count_data(self, condition={}, options={}, **kwargs):
        """ options = { 'limit': None, 'offset': None, 'page': None, 'order_by': None, 'group_by': None } """
        columns = ['COUNT(*)']
        condition = condition.copy()
        options = options.copy()
        self.qb.select(columns)
        self.qb.where(condition=condition, active=kwargs.get('active', self.active), table_active=kwargs.get('table_active', self.table))
        if options.get('keyword'):
            self.qb.like(kwargs.get('search_fields', self.search_fields), options['keyword'])
        return self.model_connect.execute_get(self.qb.get_sql(), False)['count']
    
    def get_raw_data(self, columns=[], condition={}, options={}, is_list=False, **kwargs):
        """ options = { 'limit': None, 'offset': None, 'page': None, 'order_by': None, 'group_by': None } """
        columns = self.qb.convert_column(columns)
        condition = condition.copy()
        options = options.copy()
        self.qb.select(columns)
        self.qb.where(condition=condition, active=kwargs.get('active', self.active), table_active=kwargs.get('table_active', self.table))
        if options.get('keyword'):
            self.qb.like(kwargs.get('search_fields', self.search_fields), options['keyword'])
        self.qb.extend(options)
        return self.model_connect.execute_get(self.qb.get_sql(), is_list)
    
    def create_data(self, params: dict, get_id=False, is_commit=True):
        res = None
        params = params.copy()
        if bool(params) and isinstance(params, dict):
            if not params.get('id'):
                params['id'] = uuid()
            self.qb.insert(params, has_create_date=self.has_create_date, has_create_id=self.has_create_id)
            res = self.model_connect.execute_insert(self.qb.get_sql(), is_commit=is_commit)
            if res and get_id:
                return params['id']
        return res
    
    def create_multi_data(self, params: dict, is_commit=True):
        params = params.copy()
        if 'id' not in params:
            first_keys = list(params.keys())[0]
            len_params = len(params[first_keys])
            params['id'] = [uuid() for _ in range(0, len_params)]
        self.qb.insert(params, has_create_date=self.has_create_date, has_create_id=self.has_create_id, multi_insert=True)
        res = self.model_connect.execute_insert(self.qb.get_sql(), is_commit=is_commit)
        return res
    
    def update_data(self, condition={}, params=None, clean_params=True):
        res = None
        params = params.copy()
        if not (params and isinstance(params, dict)):
            return None
        self.qb.update(params, has_update_info=self.has_update_info, clean_params=clean_params)
        res = self.model_connect.execute_update(self.qb.get_sql())
        return res
    
    def delete_data(self, condition={}):
        res = None
        condition = condition.copy()
        if condition and isinstance(condition, dict):
            self.qb.delete()
            self.qb.where(condition, active=None)
            res = self.model_connect.execute_delete(self.qb.get_sql())
        return res
    

class MineModel(DefaultModel):
    def count_mine(self, condition={}, options={}, **kwargs):
        if not condition:
            condition = {}
        condition['user_customer_id'] = self.customer_id
        return super().count_data(condition, options, **kwargs)
    
    def get_mine(self, columns=[], condition={}, options={}, is_list=True, **kwargs):
        if not condition:
            condition = {}
        condition['user_customer_id'] = self.customer_id
        return super().get_raw_data(columns, condition, options, is_list, **kwargs)
    
    def update_data(self, condition={}, params=None, clean_params=True):
        condition['user_customer_id'] = self.customer_id
        return super().update_data(condition, params, clean_params)
    
    def create_date(self, params: dict, get_id=False, is_commit=True):
        params['user_customer_id'] = self.customer_id
        return super().create_data(params, get_id, is_commit)
    
    def delete_data(self, condition={}):
        res = None
        condition = condition.copy()
        if condition and isinstance(condition, dict):
            condition['user_customer_id'] = self.customer_id
            self.qb.delete()
            self.qb.where(condition, active=None)
            self.model_connect.execute_delete(self.qb.get_sql())
        return res