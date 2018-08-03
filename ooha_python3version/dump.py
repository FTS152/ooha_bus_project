import boto3
client = boto3.client('cognito-idp', region_name='ap-northeast-1')
authResult = client.initiate_auth(AuthFlow='USER_PASSWORD_AUTH',
AuthParameters={'USERNAME': 'username', 'PASSWORD': 'password'},
ClientId='clientid')['AuthenticationResult']
client = boto3.client('cognito-identity',
region_name='ap-northeast-1')
identityId =client.get_id(IdentityPoolId='poolid',
Logins={'cognito-idp.ap-northeast-1.amazonaws.com/ap-northeast-1_dBMEa9aFc': authResult['IdToken']})['IdentityId']
credentials =client.get_credentials_for_identity(IdentityId=identityId,
Logins={'cognito-idp.ap-northeast-1.amazonaws.com/ap-northeast-1_dBMEa9aFc': authResult['IdToken']})['Credentials']
from requests_aws4auth import AWS4Auth
awsauth = AWS4Auth(credentials['AccessKeyId'],
credentials['SecretKey'], 'ap-northeast-1', 'es',
session_token=credentials['SessionToken'])
from elasticsearch import Elasticsearch, RequestsHttpConnection
es_client = Elasticsearch(
 hosts=[{'host':
'host.es.amazonaws.com', 'port': 443}],
 http_auth=awsauth,
 use_ssl=True,
 verify_certs=True,
 connection_class=RequestsHttpConnection,
 timeout=300
)
print (es_client.info())

#search condition
res3 = es_client.search(
    body={
      'size':10000,
      'query': {
        "match_all":{}
      }
    }
)

number=[[] for i in range(9)]
for i in range(1,len(res3['hits']['hits'])):
    if( 'playerInfo' in res3['hits']['hits'][i]['_source'] ):
        if('ageRange' in res3['hits']['hits'][i]['_source']):
            number[0].append(res3['hits']['hits'][i]['_source']['routeInfo']['routeName'])
            number[1].append(res3['hits']['hits'][i]['_source']['playerInfo']['plateNumber'])
            number[2].append(res3['hits']['hits'][i]['_source']['routeInfo']['position']['latitude'])
            number[3].append(res3['hits']['hits'][i]['_source']['routeInfo']['position']['longitude'])
            number[4].append(res3['hits']['hits'][i]['_source']['gender']['value'])
            number[5].append((res3['hits']['hits'][i]['_source']['ageRange']['low']+res3['hits']['hits'][i]['_source']['ageRange']['high'])/2)           
            number[6].append(res3['hits']['hits'][i]['_source']['routeInfo']['direction'])
            number[7].append(res3['hits']['hits'][i]['_source']['timestamp'])
        else:
            number[0].append(res3['hits']['hits'][i]['_source']['routeInfo']['routeName'])
            number[1].append(res3['hits']['hits'][i]['_source']['playerInfo']['plateNumber'])
            number[2].append(res3['hits']['hits'][i]['_source']['routeInfo']['position']['latitude'])
            number[3].append(res3['hits']['hits'][i]['_source']['routeInfo']['position']['longitude'])
            number[4].append(res3['hits']['hits'][i]['_source']['gender']['value'])
            number[5].append(res3['hits']['hits'][i]['_source']['age'])           
            number[6].append(res3['hits']['hits'][i]['_source']['routeInfo']['direction'])
            number[7].append(res3['hits']['hits'][i]['_source']['timestamp'])
    else:
            continue

for i in range(0,len(number[7])):
    temp=number[7][i].split("T", 1)[1]
    number[8].append(temp.split("+", 1)[0])
    number[7][i]=number[7][i].split("T", 1)[0]

import dill
file = open('results', 'wb')
dill.dump(number,file)