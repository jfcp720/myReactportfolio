#import dependencies (libraries)
import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):

    #create names for the resources
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:671515529864:deployPortfolioTopic')
    s3 = boto3.resource('s3')


    try:
        #create names for the buckets
        portfolio_bucket = s3.Bucket('portfolio.flowworkconsulting.com')
        build_bucket = s3.Bucket('portfoliobuild.flowworkconsulting.com')

        #store object in memory
        portfolio_zip = StringIO.StringIO()

        #download the zipfile to object in memory
        build_bucket.download_fileobj('portfoliobuild.zip',portfolio_zip)

        #extract the files, upload them and set the ACL permissions
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        print 'Job done!'
        topic.publish(Subject='Portfolio Deployed', Message='Portfolio deployed successfully.')
    except:
        topic.publish(Subject="Portfolio Deploy Failed", Message='The Portfolio was not deployed successfully! :(')
        raise
    return 'Hello from Lambda'
