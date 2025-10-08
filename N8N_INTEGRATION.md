# n8n Integration Guide

This guide explains how to integrate the Text-to-Video AI with n8n workflows.

## 🚀 Quick Start

### 1. Start the API Server
```bash
cd "/Users/jasonbrander/text to/Text-To-Video-AI"
python3 n8n_api.py
```

The API will be available at `http://localhost:5000`

### 2. Test the Integration
```bash
python3 test_n8n_api.py
```

## 📡 API Endpoints

### Health Check
- **GET** `/health`
- **Response:** Server status and version

### Start Video Generation
- **POST** `/generate-video`
- **Body:** `{"text": "Your topic here"}`
- **Response:** Job ID and status URLs

### Check Job Status
- **GET** `/job-status/{job_id}`
- **Response:** Current progress and status

### Download Video
- **GET** `/download-video/{job_id}`
- **Response:** Video file (MP4)

### List All Jobs
- **GET** `/jobs`
- **Response:** All jobs and their status

### Clean Up Job
- **DELETE** `/cleanup/{job_id}`
- **Response:** Confirmation of cleanup

## 🔄 n8n Workflow Integration

### Step 1: HTTP Request Node (Start Video)
- **Method:** POST
- **URL:** `http://localhost:5000/generate-video`
- **Headers:** `Content-Type: application/json`
- **Body:** 
```json
{
  "text": "{{ $json.topic }}"
}
```

### Step 2: Wait Node
- **Wait Time:** 30 seconds (adjust based on video length)

### Step 3: HTTP Request Node (Check Status)
- **Method:** GET
- **URL:** `http://localhost:5000/job-status/{{ $json.job_id }}`

### Step 4: IF Node (Check if Complete)
- **Condition:** `{{ $json.status === 'completed' }}`

### Step 5: HTTP Request Node (Download Video)
- **Method:** GET
- **URL:** `http://localhost:5000/download-video/{{ $json.job_id }}`
- **Response Format:** File

### Step 6: Clean Up (Optional)
- **Method:** DELETE
- **URL:** `http://localhost:5000/cleanup/{{ $json.job_id }}`

## 📊 Job Status Values

- **queued:** Job is waiting to start
- **processing:** Video is being generated
- **completed:** Video is ready for download
- **error:** Something went wrong

## 🔧 Configuration

### Environment Variables
Make sure these are set in your `.env` file:
```bash
OPENAI_KEY=your-openai-key
PEXELS_KEY=your-pexels-key
ELEVENLABS_API_KEY=your-elevenlabs-key
```

### API Settings
- **Host:** `0.0.0.0` (accessible from n8n)
- **Port:** `5000`
- **CORS:** Enabled for n8n integration

## 🎯 Example n8n Workflow

```json
{
  "nodes": [
    {
      "name": "Start Video Generation",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:5000/generate-video",
        "headers": {
          "Content-Type": "application/json"
        },
        "body": {
          "text": "{{ $json.topic }}"
        }
      }
    },
    {
      "name": "Wait for Processing",
      "type": "n8n-nodes-base.wait",
      "parameters": {
        "amount": 30,
        "unit": "seconds"
      }
    },
    {
      "name": "Check Status",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "GET",
        "url": "http://localhost:5000/job-status/{{ $json.job_id }}"
      }
    },
    {
      "name": "Is Complete?",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "{{ $json.status }}",
              "operation": "equal",
              "value2": "completed"
            }
          ]
        }
      }
    },
    {
      "name": "Download Video",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "GET",
        "url": "http://localhost:5000/download-video/{{ $json.job_id }}",
        "responseFormat": "file"
      }
    }
  ]
}
```

## 🚨 Error Handling

### Common Errors
- **400 Bad Request:** Missing or invalid input text
- **404 Not Found:** Job ID doesn't exist
- **500 Internal Server Error:** API key issues or processing errors

### Retry Logic
For production use, implement retry logic in n8n:
- Retry failed requests with exponential backoff
- Handle timeout scenarios
- Clean up failed jobs

## 🔒 Security Considerations

- **API Keys:** Store securely in environment variables
- **Network:** Consider using HTTPS in production
- **Access Control:** Add authentication if needed
- **Rate Limiting:** Implement if handling multiple requests

## 📈 Performance Tips

- **Concurrent Jobs:** API supports multiple simultaneous video generations
- **Memory Management:** Jobs are cleaned up after completion
- **File Storage:** Videos are stored temporarily and cleaned up
- **Monitoring:** Use `/health` endpoint for monitoring

## 🐛 Troubleshooting

### API Not Starting
- Check if port 5000 is available
- Verify all dependencies are installed
- Check environment variables are set

### Video Generation Failing
- Verify API keys are valid
- Check internet connection for Pexels videos
- Monitor server logs for errors

### n8n Connection Issues
- Ensure API server is running
- Check firewall settings
- Verify CORS is enabled

## 📞 Support

For issues or questions:
1. Check the logs in the terminal running the API
2. Test with the provided test script
3. Verify all environment variables are set correctly
4. Check n8n workflow configuration
