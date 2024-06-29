import redis
# Replace with your Redis Labs connection details
try:
    # Connect to the Redis database
    r = redis.Redis(
        host='redis-10035.c244.us-east-1-2.ec2.redns.redis-cloud.com',
        port=10035,
        password='3hb0cIGsY9X6XWnX1xUdK6uaYNElZ5XF')

    # Flush the database
    r.flushdb()
    print('Django Cache Cleared')
    print("Database flushed successfully.")

except Exception as e:
    print(f"Error: {e}")
