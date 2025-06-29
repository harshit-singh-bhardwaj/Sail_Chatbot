# SAIL Generative AI Chatbot

A Generative AI-powered chatbot developed as a final-year project for **Steel Authority of India Ltd (SAIL)**. This system provides intelligent, context-aware responses using natural language understanding and OpenAI's GPT-based models. The chatbot offers an interactive and scalable solution for internal support or customer-facing use cases.

---

## 🚀 Features

- 🔍 Natural Language Understanding using OpenAI GPT
- 👥 User registration, login, password reset
- 🧠 Trained on organization-specific FAQs (CSV-based)
- 📊 Admin dashboard to manage users and access logs
- 🧱 Modular backend with model integration and data handling
- 🎨 Clean UI built with HTML, CSS, and JavaScript
- 🗂️ Local SQLite database for user management

---

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask / Streamlit)
- **AI**: OpenAI GPT API
- **Database**: SQLite
- **Version Control**: Git & GitHub

---

## 📁 Project Structure

```plaintext
sail_chatbot/
├── app.py                      # Main app logic
├── config.py                   # Configuration and API keys
├── database.py                 # Database connection and queries
├── model/
│   ├── chatbot_model.py        # Custom response handler
│   └── model.pkl               # (Optional) Pickled model
├── templates/                  # HTML templates
├── static/                     # Static files (CSS, JS, images)
├── data/
│   └── sail_faq.csv            # Organization-specific training data
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
└── .gitignore                  # Git ignore rules
```
---

## 🧪 How to Run Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/harshit-singh-bhardwaj/Sail_Chatbot.git
   cd Sail_Chatbot

2. **Create and activate virtual environment**
   ```
   python3 -m venv venv
   source venv/bin/activate     # On Windows: venv\Scripts\activate

3. **Install dependencies**
   ```
   pip install -r requirements.txt

4. **Add your OpenAI API key**
   ```
   Open config.py and set your API key:
     - OPENAI_API_KEY = "your-api-key-here"

5. **Run the app**
   ```
   streamlit run app.py
   or (if Flask-based):
   python app.py

---

## 📸 Screenshots
  
### 🔐 User Login
![User Login](images/image.png)

### 🤖 Chatbot Interface
![Chatbot Interface](images/image_copy.png)
![Chatbot Interface](images/image_copy_2.png)

### 🤖 Chatbot
![Chatbot](images/image_copy_3.png)
![Chatbot](images/image_copy_4.png)

### 📊 Create Account
![Create Account](images/image_copy_5.png)

### 🔐 Admin Login
![Admin Login](images/image_copy_6.png)

### 📊 Admin Dashboard
![Dashboard](images/image_copy_7.png)

### 📝 Account Request
![Account Request](images/image_copy_8.png)

### ⏳ Pending Password Requests
![Pending Password Requests](images/image_copy_9.png)

### ✅ Completed Password Requests
![Completed Password Requests](images/image_copy_10.png)

### ❌ Rejected Password Requests
![Rejected Password Requests](images/image_copy_11.png)

---

## 📜 License
  - This project was built for academic and internal demonstration purposes only.
  - All rights reserved © Harshit Singh Bhardwaj.

---

## 🙌 Acknowledgements
  - OpenAI for their powerful language models
  - SAIL for the domain inspiration and context
