var button = document.getElementById("submit");

function checkUsername() {
    var input = document.getElementById("username")
    var message = document.getElementById("username-validation-warning-message")

    if(input.value == ""){
        message.textContent = "Name cannot be left blank"
        button.disabled = true;
    } else{
        message.textContent = ""
        button.disabled = false;
    }
};

function checkPassword(){
    var input = document.getElementById("password")
    var message = document.getElementById("password-validation-warning-message")

    if(input.value == ""){
        message.textContent = "Password must not be left blank"
        button.disabled = true;
    }
    else if(input.length <= 8 || input.length >= 30){
        message.textContent = "Password should be at least 8 digits and no more than 30 digits in length"
        button.disabled = true;
    } else{
        message.textContent = ""
        button.disabled = false;
    }
};

function checkPasswordConfirmation(){
    var initialPassword = document.getElementById("password")
    var confirmPassword = document.getElementById("cpassword")
    var message = document.getElementById("cpassword-validation-warning-message")

    if(initialPassword.value != confirmPassword.value){
        message.textContent = "Password and confirmation do not match"
        button.disabled = true;
    } else{
        message.textContent = ""
        button.disabled = false;
    }
};
