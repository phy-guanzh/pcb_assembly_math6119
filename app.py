import streamlit as st
import subprocess
import tempfile
import os
import pandas as pd

st.title("PCB Assembly Simulator (machine_sim.py)")

st.markdown("""
App from **Consultancy Buddies** Group  
Three examples are provided — you can update them and then upload to check the new results.
""")

solution_dir = "./solution"

for name in ["machineA.csv", "machineB.csv", "machineC.csv"]:
    file_path = os.path.join(solution_dir, name)
    if os.path.exists(file_path):
        st.subheader(f"📄 {name}")
        df = pd.read_csv(file_path)
        #st.dataframe(df)

        #Download
        with open(file_path, "rb") as f:
            st.download_button(
                label=f"⬇️ Download {name}",
                data=f,
                file_name=name,
                mime="text/csv"
            )
    else:
        st.warning(f"{name} not found.")


uploaded_files = st.file_uploader("Upload strategy files (A/B/C)", accept_multiple_files=True, type=["csv"])

if uploaded_files:
    with tempfile.TemporaryDirectory() as tmpdir:
        for f in uploaded_files:
            file_path = os.path.join(tmpdir, f.name)
            with open(file_path, "wb") as out_file:
                out_file.write(f.read())
        st.success("Files uploaded and saved.")

        if st.button("Run machine_sim"):
            cmd = ["python3", "./machine_sim.py", "--strategy_folder", tmpdir]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            st.subheader("Simulation Output")
            st.code(result.stdout)

            if result.stderr:
                st.subheader("Errors / Warnings")
                st.code(result.stderr)

