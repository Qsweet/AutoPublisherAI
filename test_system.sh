#!/bin/bash

# AutoPublisher AI - System Testing Script
# This script tests all services and their endpoints

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URLs
AUTH_URL="http://localhost:8005"
CONTENT_URL="http://localhost:8001"
PUBLISHING_URL="http://localhost:8002"
ORCHESTRATOR_URL="http://localhost:8003"
STRATEGY_URL="http://localhost:8004"

# Test credentials
TEST_EMAIL="test@example.com"
TEST_PASSWORD="TestPassword123!"
TEST_NAME="Test User"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}AutoPublisher AI - System Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print test result
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
    fi
}

# Function to test endpoint
test_endpoint() {
    local url=$1
    local name=$2
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$response" -eq 200 ]; then
        print_result 0 "$name: OK (HTTP $response)"
        return 0
    else
        print_result 1 "$name: FAILED (HTTP $response)"
        return 1
    fi
}

# Test 1: Check if services are running
echo -e "${YELLOW}Test 1: Checking if services are running...${NC}"
echo ""

test_endpoint "$AUTH_URL/health" "Auth Service"
test_endpoint "$CONTENT_URL/health" "Content Service"
test_endpoint "$PUBLISHING_URL/health" "Publishing Service"
test_endpoint "$ORCHESTRATOR_URL/health" "Orchestrator Service"
test_endpoint "$STRATEGY_URL/health" "Strategy Service"

echo ""

# Test 2: Check API documentation
echo -e "${YELLOW}Test 2: Checking API documentation...${NC}"
echo ""

test_endpoint "$AUTH_URL/docs" "Auth Service Docs"
test_endpoint "$CONTENT_URL/docs" "Content Service Docs"
test_endpoint "$PUBLISHING_URL/docs" "Publishing Service Docs"
test_endpoint "$ORCHESTRATOR_URL/docs" "Orchestrator Service Docs"
test_endpoint "$STRATEGY_URL/docs" "Strategy Service Docs"

echo ""

# Test 3: Test Auth Service - Register
echo -e "${YELLOW}Test 3: Testing user registration...${NC}"
echo ""

REGISTER_RESPONSE=$(curl -s -X POST "$AUTH_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\",
    \"full_name\": \"$TEST_NAME\"
  }")

if echo "$REGISTER_RESPONSE" | grep -q "email"; then
    print_result 0 "User registration successful"
    echo "Response: $REGISTER_RESPONSE" | jq '.' 2>/dev/null || echo "$REGISTER_RESPONSE"
else
    print_result 1 "User registration failed"
    echo "Response: $REGISTER_RESPONSE"
fi

echo ""

# Test 4: Test Auth Service - Login
echo -e "${YELLOW}Test 4: Testing user login...${NC}"
echo ""

LOGIN_RESPONSE=$(curl -s -X POST "$AUTH_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\"
  }")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    print_result 0 "User login successful"
    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token' 2>/dev/null)
    echo "Access Token: ${ACCESS_TOKEN:0:50}..."
else
    print_result 1 "User login failed"
    echo "Response: $LOGIN_RESPONSE"
    ACCESS_TOKEN=""
fi

echo ""

# Test 5: Test Auth Service - Get User Info
if [ -n "$ACCESS_TOKEN" ]; then
    echo -e "${YELLOW}Test 5: Testing get user info...${NC}"
    echo ""
    
    USER_INFO=$(curl -s -X GET "$AUTH_URL/api/v1/auth/me" \
      -H "Authorization: Bearer $ACCESS_TOKEN")
    
    if echo "$USER_INFO" | grep -q "email"; then
        print_result 0 "Get user info successful"
        echo "User Info: $USER_INFO" | jq '.' 2>/dev/null || echo "$USER_INFO"
    else
        print_result 1 "Get user info failed"
        echo "Response: $USER_INFO"
    fi
    
    echo ""
fi

# Test 6: Test Content Service - Generate Article
echo -e "${YELLOW}Test 6: Testing article generation (this may take a while)...${NC}"
echo ""

ARTICLE_RESPONSE=$(curl -s -X POST "$CONTENT_URL/api/content/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Artificial Intelligence",
    "language": "en",
    "tone": "professional",
    "target_audience": "developers"
  }')

if echo "$ARTICLE_RESPONSE" | grep -q "title"; then
    print_result 0 "Article generation successful"
    echo "Article Title: $(echo "$ARTICLE_RESPONSE" | jq -r '.title' 2>/dev/null)"
else
    print_result 1 "Article generation failed"
    echo "Response: $ARTICLE_RESPONSE"
fi

echo ""

# Test 7: Test Strategy Service - Generate Strategy
echo -e "${YELLOW}Test 7: Testing strategy generation (this may take a while)...${NC}"
echo ""

STRATEGY_RESPONSE=$(curl -s -X POST "$STRATEGY_URL/api/strategy/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "Technology",
    "target_audience": "Developers and Tech Enthusiasts",
    "goals": ["increase_traffic", "build_authority"],
    "duration_days": 30,
    "language": "en"
  }')

if echo "$STRATEGY_RESPONSE" | grep -q "industry"; then
    print_result 0 "Strategy generation successful"
    echo "Content Ideas: $(echo "$STRATEGY_RESPONSE" | jq '.content_ideas | length' 2>/dev/null) ideas generated"
else
    print_result 1 "Strategy generation failed"
    echo "Response: $STRATEGY_RESPONSE"
fi

echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}All basic tests completed!${NC}"
echo ""
echo "Next steps:"
echo "1. Check Flower dashboard: http://localhost:5555"
echo "2. Check API docs: http://localhost:8005/docs"
echo "3. Run Dashboard: cd dashboard && npm run dev"
echo ""
echo -e "${YELLOW}Note: Some tests may fail if OpenAI API key is not configured.${NC}"
echo ""

