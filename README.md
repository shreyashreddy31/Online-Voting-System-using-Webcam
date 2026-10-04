# 🗳️ Online Voting System Using Webcam

## 🔐 Webcam-Based Voter Verification & Online Voting System

A web-based voting application that combines **Computer Vision, Machine Learning, and Flask** to verify voters through a webcam before allowing them to cast their vote.

---

## 🌟 Overview

The **Online Voting System Using Webcam** is an academic web application designed to demonstrate a secure and interactive digital voting workflow.

The system captures a voter's face using a **webcam**, processes the captured data using **OpenCV**, and identifies the voter using a **K-Nearest Neighbors (KNN)** machine learning classifier.

After successful verification, the voter can access the voting interface, select a candidate, and submit their vote. The voting information is then recorded digitally.

The project demonstrates the practical integration of **Python, Flask, OpenCV, NumPy, Scikit-learn, HTML, CSS, and JavaScript**.

---

## ✨ Features

- 📷 **Webcam-Based Face Capture**  
  Captures the voter's face through a webcam.

- 👤 **Voter Registration**  
  Registers voter information and facial data.

- 🤖 **KNN Face Recognition**  
  Uses the K-Nearest Neighbors algorithm to identify registered voters.

- 🔐 **Voter Verification**  
  Verifies the voter's identity before providing access to voting.

- 🗳️ **Online Voting**  
  Allows verified voters to select and submit their vote.

- 💾 **Digital Vote Recording**  
  Stores submitted votes in a CSV file.

- 🌐 **Flask Web Application**  
  Connects the frontend interface with the Python backend.

---

## 🔄 System Workflow

```text
        👤 Voter
           │
           ▼
   📝 Voter Registration
           │
           ▼
     📷 Webcam Capture
           │
           ▼
    💾 Store Face Data
           │
           ▼
    🔐 Voter Verification
           │
           ▼
     🤖 KNN Classifier
           │
      ┌────┴────┐
      │         │
   Verified   Not Verified
      │         │
      ▼         ▼
🗳️ Voting     ❌ Access Denied
  Interface
      │
      ▼
👆 Select Candidate
      │
      ▼
🗳️ Submit Vote
      │
      ▼
💾 Store Voting Record
