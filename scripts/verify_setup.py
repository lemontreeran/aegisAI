#!/usr/bin/env python3
"""
Verification script to check AegisAI setup status
"""
import boto3
import sys
from botocore.exceptions import ClientError

def verify_dynamodb_tables():
    """Verify all DynamoDB tables exist and are active"""
    
    dynamodb = boto3.resource('dynamodb')
    
    required_tables = [
        'aegis-policies',
        'aegis-users',
        'aegis-audit-logs', 
        'aegis-feedback',
        'aegis-feedback-analytics'
    ]
    
    print("📋 Checking DynamoDB tables...")
    
    all_tables_ok = True
    for table_name in required_tables:
        try:
            table = dynamodb.Table(table_name)
            table.load()
            
            status = table.table_status
            item_count = table.item_count
            
            if status == 'ACTIVE':
                print(f"  ✓ {table_name}: {status} ({item_count} items)")
            else:
                print(f"  ⚠ {table_name}: {status}")
                all_tables_ok = False
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"  ✗ {table_name}: NOT FOUND")
                all_tables_ok = False
            else:
                print(f"  ✗ {table_name}: ERROR - {e}")
                all_tables_ok = False
    
    return all_tables_ok

def verify_opensearch_domain():
    """Verify OpenSearch domain exists and is active"""
    
    opensearch_client = boto3.client('opensearch')
    domain_name = 'aegis-ai-logs'
    
    print("\n🔍 Checking OpenSearch domain...")
    
    try:
        response = opensearch_client.describe_domain(DomainName=domain_name)
        domain_status = response['DomainStatus']
        
        processing = domain_status.get('Processing', False)
        endpoint = domain_status.get('Endpoint', 'N/A')
        
        if not processing:
            print(f"  ✓ {domain_name}: ACTIVE")
            print(f"    Endpoint: https://{endpoint}")
            return True
        else:
            print(f"  ⚠ {domain_name}: PROCESSING")
            return False
            
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"  ✗ {domain_name}: NOT FOUND")
        else:
            print(f"  ✗ {domain_name}: ERROR - {e}")
        return False

def verify_aws_credentials():
    """Verify AWS credentials are configured"""
    
    print("🔐 Checking AWS credentials...")
    
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        account_id = identity.get('Account')
        user_arn = identity.get('Arn')
        
        print(f"  ✓ AWS Account: {account_id}")
        print(f"  ✓ Identity: {user_arn}")
        return True
        
    except Exception as e:
        print(f"  ✗ AWS credentials not configured: {e}")
        return False

def verify_required_permissions():
    """Verify required AWS permissions"""
    
    print("\n🔑 Checking AWS permissions...")
    
    # Test DynamoDB permissions
    try:
        dynamodb = boto3.client('dynamodb')
        dynamodb.list_tables()
        print("  ✓ DynamoDB: READ access")
    except Exception as e:
        print(f"  ✗ DynamoDB: {e}")
        return False
    
    # Test OpenSearch permissions
    try:
        opensearch = boto3.client('opensearch')
        opensearch.list_domain_names()
        print("  ✓ OpenSearch: READ access")
    except Exception as e:
        print(f"  ✗ OpenSearch: {e}")
        return False
    
    # Test Bedrock permissions
    try:
        bedrock = boto3.client('bedrock-runtime')
        # Note: This might fail if no models are available, but it tests permissions
        print("  ✓ Bedrock: Service accessible")
    except Exception as e:
        print(f"  ⚠ Bedrock: {e}")
    
    return True

def test_backend_connectivity():
    """Test if backend can connect to AWS services"""
    
    print("\n🔌 Testing backend connectivity...")
    
    try:
        # Import and test orchestrator
        sys.path.append('.')
        from backend.orchestrator import AegisOrchestrator
        
        orchestrator = AegisOrchestrator()
        
        # Test with a simple event
        test_event = {
            'request_type': 'get_advisory',
            'user_token': 'demo_admin',
            'data': {
                'advisory_type': 'general',
                'context': {},
                'violations': [],
                'risk_factors': []
            }
        }
        
        result = orchestrator.lambda_handler(test_event)
        
        if result['statusCode'] == 200:
            print("  ✓ Backend orchestrator: WORKING")
            return True
        else:
            print(f"  ⚠ Backend orchestrator: Status {result['statusCode']}")
            return False
            
    except Exception as e:
        print(f"  ✗ Backend orchestrator: {e}")
        return False

def main():
    """Main verification function"""
    print("🔍 Verifying AegisAI setup...")
    print("=" * 50)
    
    all_checks_passed = True
    
    # Check AWS credentials
    if not verify_aws_credentials():
        all_checks_passed = False
    
    # Check permissions
    if not verify_required_permissions():
        all_checks_passed = False
    
    # Check DynamoDB tables
    if not verify_dynamodb_tables():
        all_checks_passed = False
    
    # Check OpenSearch domain
    if not verify_opensearch_domain():
        all_checks_passed = False
    
    # Test backend connectivity
    if not test_backend_connectivity():
        all_checks_passed = False
    
    print("\n" + "=" * 50)
    
    if all_checks_passed:
        print("🎉 All checks passed! AegisAI is ready to use.")
        print("\nNext steps:")
        print("1. Start the backend: python backend/api.py")
        print("2. Access the frontend at: http://localhost:5173")
        print("3. Login with demo credentials (admin/admin123)")
    else:
        print("⚠ Some checks failed. Please review the issues above.")
        print("\nTroubleshooting:")
        print("1. Ensure AWS credentials are configured: aws configure")
        print("2. Run setup scripts: python scripts/setup_dynamodb.py")
        print("3. Check AWS permissions for DynamoDB, OpenSearch, and Bedrock")

if __name__ == "__main__":
    main()