# 🚀 QUICK REFERENCE — CropGuard AI

## START HERE (Copy & Paste)

### 1. Backend Setup (Terminal 1)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
✅ Runs on http://localhost:5000

### 2. Frontend Setup (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```
✅ Runs on http://localhost:3000

### 3. Login
- Username: `admin`
- Password: `Admin@123`

---

## BEFORE YOU SUBMIT

### Train the Model (REQUIRED!)
1. Download PlantVillage from Kaggle
2. Run from backend folder:
```bash
python model/train.py --data_dir /path/to/plantvillage/color --model_type mobilenet --epochs 30 --fine_tune
```
3. Wait 30-60 minutes (GPU) or 2-3 hours (CPU)
4. Check: `ls backend/model/saved_model/crop_cnn.h5` exists

### Test the App
1. Upload a leaf image → See prediction ✅
2. Check user history → See scan gallery ✅
3. Login as admin → See dashboard ✅
4. Make a prediction → See alert bell ✅

---

## KEY FILES TO SHOW IN DEMO

| File | Purpose |
|------|---------|
| `backend/model/train.py` | Training script (run this!) |
| `backend/model/cnn_model.py` | CNN architectures |
| `backend/routes/user_routes.py` | API endpoints |
| `frontend/src/pages/Home.jsx` | Upload interface |
| `frontend/src/pages/Result.jsx` | Prediction display |
| `config.py` | 38 diseases + recommendations |
| `COMPLETE_GUIDE.md` | Full documentation |

---

## API ENDPOINTS (For Integration Testing)

```bash
# Test prediction
curl -X POST http://localhost:5000/api/predict \
  -F "leaf_image=@leaf.jpg"

# Get result
curl http://localhost:5000/api/result/1

# Get user history
curl -b cookies.txt http://localhost:5000/api/history

# Admin dashboard
curl -b cookies.txt http://localhost:5000/api/admin/dashboard
```

---

## EMAIL ALERTS (Optional)

1. Create `backend/.env`:
```
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-app-password
```

2. Test: Make a prediction → Email should arrive

---

## WHAT'S INCLUDED

✅ Flask REST API (complete)
✅ React Frontend (complete)
✅ TensorFlow/Keras CNN (ready to train)
✅ Email Alert System (complete)
✅ In-app Notification Bell (complete)
✅ Admin Dashboard (complete)
✅ User Authentication (complete)
✅ Database Models (complete)

## WHAT YOU NEED TO DO

1️⃣ **Train the model** (most important!)
   ```bash
   python model/train.py --data_dir ... --model_type mobilenet --epochs 30
   ```

2️⃣ **Run both backend & frontend**
   ```bash
   # Terminal 1: python app.py
   # Terminal 2: npm run dev
   ```

3️⃣ **Test the app**
   - Upload image → Predict
   - Check history
   - Check alerts
   - Check admin dashboard

4️⃣ **Show in demo**
   - Home (upload)
   - Result (disease + confidence)
   - History (scan gallery)
   - Admin Dashboard (metrics)
   - Alerts (notification bell)

---

## 📊 EXPECTED RESULTS

After training your model:
- Validation Accuracy: 93-96%
- Inference Time: 0.2-0.4 seconds
- Top-3 Predictions: Shows all likely diseases
- Recommendation: Treatment advice based on disease

---

## 🆘 STUCK?

1. Backend won't start?
   → Check Python 3.8+, all dependencies installed

2. Frontend won't start?
   → Check Node 16+, all npm packages installed

3. Prediction fails?
   → Model not trained! Run training script first

4. API 404 error?
   → Check backend is running on :5000

5. CORS errors?
   → Vite proxy configured automatically, check console

---

**Read COMPLETE_GUIDE.md for full documentation**

**Questions? Check troubleshooting section!**

**Ready to deploy? You've got this! 🌿**
