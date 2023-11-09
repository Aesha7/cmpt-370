import React, { useState, useEffect } from "react";
import { Route, Routes, useNavigate, useLocation } from "react-router";
import "../style/CoachStudentsListPage.css";

const server_URL = "http://127.0.0.1:5000/"; //URL to access server

const CoachStudentsListPage = () => {

  let userID;
  const [staffLevel, setStaffLevel] = useState("");

  let navigate = useNavigate();

  const goBack = () =>{
    let path = "/my-account";
    navigate(path, {state:userID})
  }

  // uncovering the page if a valid account
  if(staffLevel >= 1){
    document.getElementById("overlay").style.display = "none";
  }

  return (
    <div className="coach-page">
      <div className="top-bar">
        Students List
        <div className="allButtons">
        <button className="top-bar-button" onClick={goBack}>Back</button>
        </div>
      </div>
      <div className="overlay" id="overlay">YOU DO NOT HAVE ACCESS TO THIS PAGE!</div>
    </div>
        );

};
export default CoachStudentsListPage