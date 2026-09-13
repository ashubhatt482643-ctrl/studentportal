import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import hashlib
import re

# Set page config
st.set_page_config(
    page_title="Student Enrollment Portal - NIA",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    .step-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .info-box {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    .success-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4CAF50;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    .error-box {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}

# Create data directory for storing submissions
if not os.path.exists('student_data'):
    os.makedirs('student_data')
if not os.path.exists('student_uploads'):
    os.makedirs('student_uploads')

# ==================== HELPER FUNCTIONS ====================

def hash_password(password):
    """Hash password for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate Indian phone number"""
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, phone) is not None

def validate_aadhar(aadhar):
    """Validate Aadhar format"""
    pattern = r'^\d{12}$'
    return re.match(pattern, aadhar.replace(" ", "").replace("-", "")) is not None

def load_user_data(email):
    """Load user data from file"""
    file_path = f'student_data/{email}.json'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_user_data(email, data):
    """Save user data to file"""
    file_path = f'student_data/{email}.json'
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def check_user_exists(email):
    """Check if user already registered"""
    return os.path.exists(f'student_data/{email}.json')

def get_file_size_mb(file_obj):
    """Get file size in MB"""
    return len(file_obj.getvalue()) / (1024 * 1024)

# ==================== LOGIN & REGISTRATION ====================

def login_page():
    """Login and Registration Page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center; color: #667eea;'>📚 NIA Student Portal</h1>", 
                   unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #764ba2;'>राष्ट्रीय लेखाकार संस्थान</h3>", 
                   unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        # LOGIN TAB
        with tab1:
            st.markdown("<div class='step-header'><h3>Login to Your Account</h3></div>", 
                       unsafe_allow_html=True)
            
            login_email = st.text_input("Email Address", placeholder="your.email@example.com", key="login_email")
            login_password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")
            
            if st.button("🔓 Login", use_container_width=True, key="login_btn"):
                if not login_email or not login_password:
                    st.error("❌ Please fill in all fields")
                elif not validate_email(login_email):
                    st.error("❌ Invalid email format")
                else:
                    user_data = load_user_data(login_email)
                    if user_data and user_data['password'] == hash_password(login_password):
                        st.session_state.logged_in = True
                        st.session_state.user_data = user_data
                        st.session_state.form_data = user_data.get('form_data', {})
                        st.session_state.current_step = user_data.get('current_step', 1)
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password")
        
        # REGISTRATION TAB
        with tab2:
            st.markdown("<div class='step-header'><h3>Create New Account</h3></div>", 
                       unsafe_allow_html=True)
            
            reg_email = st.text_input("Email Address", placeholder="your.email@example.com", key="reg_email")
            reg_password = st.text_input("Password", type="password", placeholder="Create a password", key="reg_pass")
            reg_password_confirm = st.text_input("Confirm Password", type="password", 
                                                 placeholder="Confirm your password", key="reg_pass_conf")
            
            if st.button("📝 Register", use_container_width=True, key="register_btn"):
                if not reg_email or not reg_password or not reg_password_confirm:
                    st.error("❌ Please fill in all fields")
                elif not validate_email(reg_email):
                    st.error("❌ Invalid email format")
                elif len(reg_password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                elif reg_password != reg_password_confirm:
                    st.error("❌ Passwords do not match")
                elif check_user_exists(reg_email):
                    st.error("❌ Email already registered")
                else:
                    new_user = {
                        'email': reg_email,
                        'password': hash_password(reg_password),
                        'registration_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'current_step': 1,
                        'form_data': {},
                        'submitted': False
                    }
                    save_user_data(reg_email, new_user)
                    st.success("✅ Registration successful! Please login now.")
                    st.rerun()

# ==================== ENROLLMENT FORM STEPS ====================

def step_1_instructions():
    """Step 1: Instructions"""
    st.markdown("<div class='step-header'><h3>Step 1️⃣ : Instructions / निर्देश</h3></div>", 
               unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class='info-box'>
        <h4>📋 कृपया आवेदन पत्र भरने से पूर्व दिशा निर्देश, Notification, Fees schedule, College List एवं University website का अवलोकन करें।</h4>
        <p><strong>Please review all instructions, notifications, fee schedules, and college/university details before proceeding.</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("ℹ️ **Important Notes:**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        1. ✅ Complete all 5 steps carefully
        2. ✅ Your information will be saved at each step
        3. ✅ Upload clear and readable documents
        4. ✅ Review all information before final submission
        """)
    
    with col2:
        st.markdown("""
        5. ✅ You can edit your details before final confirmation
        6. ✅ Application must be submitted completely
        7. ✅ Keep your admit card for reference
        8. ✅ Support: contact@nia.edu.in
        """)
    
    st.markdown("<div class='info-box'><strong>Accepted File Formats:</strong> JPG, PNG, PDF (Max 5MB each)</div>", 
               unsafe_allow_html=True)
    
    if st.button("✅ I have read all instructions - Proceed to Step 2", use_container_width=True):
        st.session_state.current_step = 2
        st.rerun()

def step_2_personal_info():
    """Step 2: Personal Information"""
    st.markdown("<div class='step-header'><h3>Step 2️⃣ : Personal Information / व्यक्तिगत जानकारी</h3></div>", 
               unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Basic Information")
        form_data = st.session_state.form_data
        
        full_name = st.text_input(
            "Full Name / पूरा नाम *",
            value=form_data.get('full_name', ''),
            placeholder="Enter your full name"
        )
        
        email = st.text_input(
            "Email Address *",
            value=st.session_state.user_data.get('email', ''),
            disabled=True,
            placeholder="your.email@example.com"
        )
        
        phone = st.text_input(
            "Mobile Number (10 digits) / मोबाइल नंबर *",
            value=form_data.get('phone', ''),
            placeholder="98XXXXXXXX"
        )
    
    with col2:
        st.subheader("🆔 Identity Information")
        
        dob = st.date_input(
            "Date of Birth / जन्म तिथि *",
            value=pd.to_datetime(form_data.get('dob', '')).date() if form_data.get('dob') else None
        )
        
        aadhar = st.text_input(
            "Aadhar Number (12 digits) / आधार नंबर *",
            value=form_data.get('aadhar', ''),
            placeholder="XXXX XXXX XXXX"
        )
        
        gender = st.selectbox(
            "Gender / लिंग *",
            ["Select", "Male / पुरुष", "Female / महिला", "Other / अन्य"],
            index=["Select", "Male / पुरुष", "Female / महिला", "Other / अन्य"].index(form_data.get('gender', 'Select'))
        )
    
    st.divider()
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🏠 Address Information")
        
        address = st.text_area(
            "Complete Address / पूरा पता *",
            value=form_data.get('address', ''),
            placeholder="Street address, City, State, PIN"
        )
        
        city = st.text_input(
            "City / शहर *",
            value=form_data.get('city', ''),
            placeholder="Your city"
        )
    
    with col4:
        st.subheader("🎓 Educational Background")
        
        state = st.text_input(
            "State / राज्य *",
            value=form_data.get('state', ''),
            placeholder="Your state"
        )
        
        qualification = st.selectbox(
            "Highest Qualification / शैक्षणिक योग्यता *",
            ["Select", "12th Pass", "Bachelor's Degree", "Master's Degree", "Other"],
            index=["Select", "12th Pass", "Bachelor's Degree", "Master's Degree", "Other"].index(form_data.get('qualification', 'Select'))
        )
    
    # Validation and Save
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("⬅️ Back to Step 1", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()
    
    with col_btn2:
        if st.button("✅ Save & Continue to Step 3", use_container_width=True):
            # Validation
            errors = []
            if not full_name: errors.append("Full Name is required")
            if not phone: errors.append("Phone number is required")
            elif not validate_phone(phone): errors.append("Invalid phone number (10 digits required)")
            if not dob: errors.append("Date of Birth is required")
            if not aadhar: errors.append("Aadhar number is required")
            elif not validate_aadhar(aadhar): errors.append("Invalid Aadhar format (12 digits required)")
            if gender == "Select": errors.append("Please select gender")
            if not address: errors.append("Address is required")
            if not city: errors.append("City is required")
            if not state: errors.append("State is required")
            if qualification == "Select": errors.append("Please select qualification")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Save form data
                st.session_state.form_data.update({
                    'full_name': full_name,
                    'phone': phone,
                    'dob': str(dob),
                    'aadhar': aadhar,
                    'gender': gender,
                    'address': address,
                    'city': city,
                    'state': state,
                    'qualification': qualification
                })
                
                user_data = st.session_state.user_data
                user_data['form_data'] = st.session_state.form_data
                user_data['current_step'] = 3
                save_user_data(user_data['email'], user_data)
                
                st.success("✅ Step 2 completed successfully!")
                st.session_state.current_step = 3
                st.rerun()

def step_3_document_upload():
    """Step 3: Document Upload"""
    st.markdown("<div class='step-header'><h3>Step 3️⃣ : Upload Documents / दस्तावेज़ अपलोड करें</h3></div>", 
               unsafe_allow_html=True)
    
    st.info("📄 **Required Documents:** Photo | Signature | Previous Marksheet | Aadhaar Card\n\n**Formats:** JPG, PNG, PDF | **Max Size:** 5MB each")
    
    form_data = st.session_state.form_data
    uploads_dir = f"student_uploads/{st.session_state.user_data['email']}"
    
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    
    # Define required documents
    required_docs = {
        'photo': {'name': 'Passport Photo / फोटो', 'type': 'photo'},
        'signature': {'name': 'Digital Signature / हस्ताक्षर', 'type': 'signature'},
        'marksheet': {'name': 'Previous Marksheet / अंकतालिका', 'type': 'marksheet'},
        'aadhar': {'name': 'Aadhaar Card / आधार कार्ड', 'type': 'aadhar'}
    }
    
    upload_status = {}
    
    for doc_key, doc_info in required_docs.items():
        with st.expander(f"📎 {doc_info['name']}", expanded=False):
            uploaded_file = st.file_uploader(
                f"Upload {doc_info['name']}",
                type=['jpg', 'jpeg', 'png', 'pdf'],
                key=f"upload_{doc_key}"
            )
            
            if uploaded_file is not None:
                file_size = get_file_size_mb(uploaded_file)
                
                if file_size > 5:
                    st.error(f"❌ File size ({file_size:.2f}MB) exceeds 5MB limit")
                    upload_status[doc_key] = False
                else:
                    file_path = os.path.join(uploads_dir, f"{doc_key}_{uploaded_file.name}")
                    with open(file_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    st.success(f"✅ {uploaded_file.name} uploaded successfully ({file_size:.2f}MB)")
                    upload_status[doc_key] = True
                    form_data[f'{doc_key}_file'] = uploaded_file.name
            
            # Show existing file
            if form_data.get(f'{doc_key}_file'):
                st.caption(f"📁 Current file: {form_data.get(f'{doc_key}_file')}")
    
    st.divider()
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("⬅️ Back to Step 2", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()
    
    with col_btn2:
        if st.button("✅ Continue to Step 4 (Preview)", use_container_width=True):
            required_uploads = ['photo', 'signature', 'marksheet', 'aadhar']
            missing = [doc for doc in required_uploads if not form_data.get(f'{doc}_file')]
            
            if missing:
                st.error(f"❌ Please upload all required documents")
            else:
                user_data = st.session_state.user_data
                user_data['form_data'] = st.session_state.form_data
                user_data['current_step'] = 4
                save_user_data(user_data['email'], user_data)
                
                st.success("✅ All documents uploaded successfully!")
                st.session_state.current_step = 4
                st.rerun()

def step_4_preview():
    """Step 4: Preview Information"""
    st.markdown("<div class='step-header'><h3>Step 4️⃣ : Preview Application / अनुप्रयोग की समीक्षा करें</h3></div>", 
               unsafe_allow_html=True)
    
    form_data = st.session_state.form_data
    user_email = st.session_state.user_data['email']
    
    # Personal Information Review
    with st.expander("👤 Personal Information", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Full Name", form_data.get('full_name', 'N/A'))
            st.metric("Email", user_email)
            st.metric("Phone", form_data.get('phone', 'N/A'))
        with col2:
            st.metric("Date of Birth", form_data.get('dob', 'N/A'))
            st.metric("Gender", form_data.get('gender', 'N/A').split('/')[0].strip())
            st.metric("Aadhar", f"****{form_data.get('aadhar', 'N/A')[-4:]}")
        with col3:
            st.metric("City", form_data.get('city', 'N/A'))
            st.metric("State", form_data.get('state', 'N/A'))
            st.metric("Qualification", form_data.get('qualification', 'N/A'))
    
    # Address Review
    with st.expander("🏠 Address Information", expanded=True):
        st.text(form_data.get('address', 'N/A'))
    
    # Documents Review
    with st.expander("📄 Uploaded Documents", expanded=True):
        doc_names = {
            'photo_file': '🖼️ Photo',
            'signature_file': '✍️ Signature',
            'marksheet_file': '📊 Marksheet',
            'aadhar_file': '🆔 Aadhaar'
        }
        
        for doc_key, doc_display in doc_names.items():
            if form_data.get(doc_key):
                st.write(f"✅ {doc_display}: {form_data.get(doc_key)}")
            else:
                st.write(f"❌ {doc_display}: Not uploaded")
    
    st.divider()
    
    # Edit Option
    if st.checkbox("✏️ Need to edit information?"):
        st.info("You can go back to the previous steps to make changes.")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("⬅️ Back to Step 3", use_container_width=True):
            st.session_state.current_step = 3
            st.rerun()
    
    with col_btn2:
        if st.button("✅ Confirm & Submit Application", use_container_width=True):
            user_data = st.session_state.user_data
            user_data['form_data'] = st.session_state.form_data
            user_data['current_step'] = 5
            user_data['submitted'] = True
            user_data['submission_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_user_data(user_email, user_data)
            
            st.session_state.current_step = 5
            st.rerun()

def step_5_confirmation():
    """Step 5: Final Confirmation"""
    st.markdown("<div class='step-header'><h3>Step 5️⃣ : Confirmation & Admit Card / पुष्टि और प्रवेश पत्र</h3></div>", 
               unsafe_allow_html=True)
    
    form_data = st.session_state.form_data
    user_data = st.session_state.user_data
    user_email = user_data['email']
    
    # Success Message
    st.markdown("""
        <div class='success-box'>
            <h3>✅ Application Submitted Successfully!</h3>
            <p>आपका आवेदन सफलतापूर्वक जमा किया गया है।</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Generate Admit Card
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📄 Admit Card / प्रवेश पत्र")
        
        admit_data = f"""
        ╔════════════════════════════════════════════════╗
        ║        NATIONAL INSTITUTE OF ACCOUNTANTS       ║
        ║              STUDENT ADMIT CARD                ║
        ╠════════════════════════════════════════════════╣
        ║                                                ║
        ║  Registration Number: {user_email[:10].upper()}    ║
        ║  Name: {form_data.get('full_name', 'N/A'):<31} ║
        ║  Email: {user_email:<38} ║
        ║  Phone: {form_data.get('phone', 'N/A'):<37} ║
        ║  DOB: {form_data.get('dob', 'N/A'):<39} ║
        ║  Submission Date: {user_data.get('submission_date', ''):<28} ║
        ║                                                ║
        ║  Status: ✅ APPROVED                           ║
        ║                                                ║
        ║  Valid Till: {(datetime.now().year + 1)}-12-31 {' '*14} ║
        ║                                                ║
        ╚════════════════════════════════════════════════╝
        """
        
        st.code(admit_data)
    
    with col2:
        st.metric("Application ID", user_email[:10].upper())
        st.metric("Status", "✅ APPROVED")
        st.metric("Submitted On", user_data.get('submission_date', 'N/A'))
    
    # Important Information
    st.info("""
    📌 **Important Information:**
    - Your admit card has been generated and can be downloaded
    - A confirmation email will be sent to your registered email
    - Keep your application ID safe for future reference
    - You will receive further instructions via email
    """)
    
    # Download Admit Card
    col_download = st.columns(3)
    with col_download[0]:
        if st.button("📥 Download Admit Card", use_container_width=True):
            st.success("Admit card download initiated")
    
    with col_download[1]:
        if st.button("📧 Send to Email", use_container_width=True):
            st.success(f"Admit card sent to {user_email}")
    
    with col_download[2]:
        if st.button("🔙 Go to Dashboard", use_container_width=True):
            st.session_state.current_step = 0
            st.rerun()
    
    st.divider()
    
    # Application Summary
    with st.expander("📋 View Complete Application Summary"):
        st.json(form_data)

def dashboard():
    """Student Dashboard"""
    user_data = st.session_state.user_data
    form_data = st.session_state.form_data
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Student Name", form_data.get('full_name', 'Not filled'))
    with col2:
        st.metric("Email", user_data.get('email', ''))
    with col3:
        status = "✅ Submitted" if user_data.get('submitted') else "🟡 In Progress"
        st.metric("Application Status", status)
    
    st.divider()
    
    # Progress Bar
    progress_step = user_data.get('current_step', 1)
    st.progress(min(progress_step / 5, 1.0))
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Continue Application", use_container_width=True):
            st.session_state.current_step = progress_step
            st.rerun()
    
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_data = {}
            st.session_state.form_data = {}
            st.success("Logged out successfully!")
            st.rerun()

# ==================== MAIN APP ====================

def main():
    # Sidebar
    with st.sidebar:
        st.markdown("### 📚 NIA Portal")
        if st.session_state.logged_in:
            st.markdown(f"**{st.session_state.user_data.get('email', 'User')}**")
            
            # Progress indicator
            progress = st.session_state.current_step
            st.markdown(f"**Progress:** Step {min(progress, 5)} / 5")
            
            with st.expander("ℹ️ Application Status"):
                st.write(f"Current Step: {min(progress, 5)}")
                st.write(f"Submitted: {'Yes ✅' if st.session_state.user_data.get('submitted') else 'No 🟡'}")
                st.write(f"Email: {st.session_state.user_data.get('email')}")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()
    
    # Main content
    if not st.session_state.logged_in:
        login_page()
    else:
        # Step indicator
        step_indicators = st.columns(5)
        steps = ['1️⃣ Info', '2️⃣ Personal', '3️⃣ Upload', '4️⃣ Preview', '5️⃣ Confirm']
        
        for i, (indicator, step_label) in enumerate(zip(step_indicators, steps)):
            with indicator:
                current = st.session_state.current_step == i + 1
                submitted = st.session_state.user_data.get('submitted', False) and i < 5
                
                if current:
                    st.markdown(f"<p style='text-align: center; background-color: #667eea; color: white; padding: 10px; border-radius: 5px;'><strong>{step_label}</strong></p>", 
                               unsafe_allow_html=True)
                elif i < st.session_state.current_step or submitted:
                    st.markdown(f"<p style='text-align: center; background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;'>✅ {step_label}</p>", 
                               unsafe_allow_html=True)
                else:
                    st.markdown(f"<p style='text-align: center; background-color: #ccc; color: #666; padding: 10px; border-radius: 5px;'>{step_label}</p>", 
                               unsafe_allow_html=True)
        
        st.divider()
        
        # Display appropriate step
        if st.session_state.current_step == 0:
            dashboard()
        elif st.session_state.current_step == 1:
            step_1_instructions()
        elif st.session_state.current_step == 2:
            step_2_personal_info()
        elif st.session_state.current_step == 3:
            step_3_document_upload()
        elif st.session_state.current_step == 4:
            step_4_preview()
        elif st.session_state.current_step == 5:
            step_5_confirmation()

if __name__ == "__main__":
    main()
