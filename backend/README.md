# Maritime Twin Backend

This is the minimum Python-to-Three.js loop for the maritime wireless digital-twin demo.

## Run

```powershell
python backend/app.py
```

Then open `Threejs海陆通信场景仿真 -场景加大版.html`. The page posts the current environment, geometry, and frequency to:

```text
http://127.0.0.1:8000/api/channel/predict
```

The backend returns path loss, delay, duct metrics, duct existence probability, co-channel interference alarm fields, receive power, and inference time. The Three.js scene uses these Python-returned duct and alarm fields when the backend is online, then falls back to the browser-side surrogate when the backend is offline.

This first backend is a fast Python surrogate, meant to be replaced or extended by PE/ray-tracing data generation and a trained multi-task AI model.

## Endpoints

```text
GET  /api/health
POST /api/channel/predict
POST /api/dataset/sample
```

`/api/dataset/sample` produces small synthetic samples for validating the data-flow shape. It is not a final research dataset generator.
