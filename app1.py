import streamlit as st
import subprocess
import tempfile
import os
import pandas as pd

st.set_page_config(page_title="PCB Assembly Simulator", layout="centered")

st.title("🔧 PCB Assembly Simulator")

st.markdown("""
App from **Consultancy Buddies** Group  
Three examples are provided — you can update them and then upload to check the new results.
""")

# -------------------------
# 1. 显示默认 machineA/B/C.csv 内容 & 下载
# -------------------------
solution_dir = "./solution"
default_files = ["machineA.csv", "machineB.csv", "machineC.csv"]

st.text("📂 Default Strategy Files (from ./solution)")

for name in default_files:
    file_path = os.path.join(solution_dir, name)
    if os.path.exists(file_path):
        st.subheader(f"📄 {name}")
        df = pd.read_csv(file_path)
        #st.dataframe(df)

        with open(file_path, "rb") as f:
            st.download_button(
                label=f"⬇️ Download {name}",
                data=f,
                file_name=name,
                mime="text/csv"
            )
    else:
        st.warning(f"{name} not found in ./solution")

# -------------------------
# 2. 文件上传（替代默认）
# -------------------------
st.header("📤 Upload Your Own Strategy Files")

uploaded_files = st.file_uploader(
    "Upload your strategy files (machineA.csv, B, C)", 
    accept_multiple_files=True, 
    type=["csv"]
)

# -------------------------
# 3. 执行 machine_sim.py
# -------------------------
if uploaded_files:
    st.success("✔️ Uploaded files detected. These will be used instead of defaults.")
    if st.button("🚀 Run machine_sim on Uploaded Files"):
        with tempfile.TemporaryDirectory() as tmpdir:
            for f in uploaded_files:
                file_path = os.path.join(tmpdir, f.name)
                with open(file_path, "wb") as out_file:
                    out_file.write(f.read())

            cmd = ["python3", "./machine_sim.py", "--strategy_folder", tmpdir]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            st.subheader("📊 Simulation Output")
            st.code(result.stdout)

            if result.stderr:
                st.subheader("⚠️ Warnings / Errors")
                st.code(result.stderr)
else:
    st.info("No uploaded files. Using default ./solution files.")
    if st.button("🚀 Run machine_sim on Default Files"):
        cmd = ["python3", "./machine_sim.py", "--strategy_folder", "./solution"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        st.subheader("📊 Simulation Output (Default)")
        st.code(result.stdout)

        if result.stderr:
            st.subheader("⚠️ Warnings / Errors")
            st.code(result.stderr)

