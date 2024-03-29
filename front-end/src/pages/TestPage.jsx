import React, { useEffect, useState } from "react";
import Container from '@material-ui/core/Container';
import Typography from '@material-ui/core/Typography';
import { Route, Routes, useNavigate } from "react-router";
import '../style/AccountCreationPage.css';
//import APIService from "../Components/APIService.jsx";
//import axios from axios;

function TestPage() {
    const [profileData,setProfile] = useState(null)

    function getData() {
        //for testing recieving data from server
        fetch("/testget")
        .then((response) => {
            const res = response.data
            setProfile(({
                name: res.name
            }))
        }).catch((error) => {
            if (error.response) {
                console.log(error.response)
                console.log(error.response.status)
                console.log(error.response.headers)
            }
        })
    }

    function testError() {
        fetch("http://127.0.0.1:5000/test_error")
        .then((response) => {console.log("hello!!")})
    }
    return (
        <div className="account-create-column-entry">
        <button className="account-create-submit-button" onClick={testError}>Submit</button>
        {/* {profileData && <div>
            <p>name: {profileData.name}</p>
            </div>
            } */}
        </div>
    )
}



export default TestPage;
