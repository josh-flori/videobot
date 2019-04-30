from googleapiclient.discovery import build
from oauth2client import file
from oauth2client.service_account import ServiceAccountCredentials


def write_to_sheet(total_list, column,service,_id):

    # Write data to sheet
    def write_values_main(_id, rng, data):
        value_input_option = 'USER_ENTERED'
        value_range_body = {
            'majorDimension': 'ROWS',
            # 'range': rng,
            'values': data
        }

    value_range_body = {
        'majorDimension': 'ROWS',
        # 'range': rng,
        'values': [[i] for i in total_list]
    }

    request = service.spreadsheets().values().update(spreadsheetId=_id,
                                                     range='Sheet1!' + column + '2',
                                                     valueInputOption='RAW',
                                                     body=value_range_body)
    response = request.execute()



