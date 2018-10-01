print("Connecting......")

import boto3
client = boto3.client('cognito-idp', region_name='ap-northeast-1')
authResult = client.initiate_auth(AuthFlow='USER_PASSWORD_AUTH',
AuthParameters={'USERNAME': '', 'PASSWORD': ''},
ClientId='2on0keh94h3u7jn5b7oci65d2u')['AuthenticationResult']
client = boto3.client('cognito-identity',
region_name='ap-northeast-1')
identityId =client.get_id(IdentityPoolId='ap-northeast-1:daed3759-c089-4347-8f1b-1639ae65e03c',
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
'search-prod-po-prodfa-rsq1nqydqzos-vhhea2hvm5zikrjmqb7h67zt4u.ap-northeast-1.es.amazonaws.com', 'port': 443}],
 http_auth=awsauth,
 use_ssl=True,
 verify_certs=True,
 connection_class=RequestsHttpConnection,
 timeout=300
)
print (es_client.info())

import sys
routeName = sys.argv[1]
direction = sys.argv[2]
date = sys.argv[3]

#search condition
res3 = es_client.search(
	body={
		'size':10000,
		"query": {
			'bool':{
				'filter':[
					{ "match": {'routeInfo.routeName' : routeName}},
					{ "match": {'routeInfo.direction' : direction}},
					{ "range": {'timestamp': {"gte":date}}}
				]
			}
		}
	}
)

number=[]
for i in range(0,len(res3['hits']['hits'])):
	if( 'playerInfo' in res3['hits']['hits'][i]['_source'] ):
		if('ageRange' in res3['hits']['hits'][i]['_source']):
			a = []
			a.append(res3['hits']['hits'][i]['_source']['routeInfo']['routeName'])
			a.append(res3['hits']['hits'][i]['_source']['playerInfo']['plateNumber'])
			a.append(res3['hits']['hits'][i]['_source']['routeInfo']['position']['latitude'])
			a.append(res3['hits']['hits'][i]['_source']['routeInfo']['position']['longitude'])
			a.append(res3['hits']['hits'][i]['_source']['gender']['value'])
			a.append((res3['hits']['hits'][i]['_source']['ageRange']['low']+res3['hits']['hits'][i]['_source']['ageRange']['high'])/2)           
			a.append(res3['hits']['hits'][i]['_source']['routeInfo']['direction'])
			a.append(res3['hits']['hits'][i]['_source']['timestamp'])
			a.append(0)
			number.append(a)
		else:
			a = []
			a.append(res3['hits']['hits'][i]['_source']['routeInfo']['routeName'])
			a.append(res3['hits']['hits'][i]['_source']['playerInfo']['plateNumber'])
			a.append(res3['hits']['hits'][i]['_source']['routeInfo']['position']['latitude'])
			a.append(res3['hits']['hits'][i]['_source']['routeInfo']['position']['longitude'])
			a.append(res3['hits']['hits'][i]['_source']['gender']['value'])
			a.append(res3['hits']['hits'][i]['_source']['age'])           
			a.append(res3['hits']['hits'][i]['_source']['routeInfo']['direction'])
			a.append(res3['hits']['hits'][i]['_source']['timestamp'])
			a.append(0)
			number.append(a)
	else:
			continue

for i in range(0,len(number)):
	temp = str(number[i][7]).split("T", 1)[1]
	number[i][8] = temp.split("+", 1)[0]
	number[i][7] = str(number[i][7]).split("T", 1)[0]

print('data count: '+str(len(number)))

import dill
file = open('results', 'wb')
dill.dump(number,file)