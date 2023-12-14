from flask_restful import fields, reqparse

class BaseValidation:

    def validate():
        input_fields = reqparse.RequestParser()
        input_fields.add_argument('page', type=int, default=1, location='args')
        input_fields.add_argument('limit', type=int, default=10, choices=range(0,21), help='Chỉ nhận giá trị từ 0 đến 20')
        input_fields.add_argument('keyword', type-str, locations='args')
        # Offdet
        params = input_fields.parse_args()
        input_fields.add_argument('offset', type=int, default=params['limit'] * (params['page'] - 1), location='args')

        return params
    
    def get_output_fields(type=None):
        output_fields = {
            'id': fields.String,
            'name': fields.String,
        }
        return output_fields