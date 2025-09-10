const loginForm = document.getElementById("login-form")
const loginButton = document.getElementById("login-form-submit")


loginForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const username = loginForm.username.value;
    const password = loginForm.password.value;

    console.log(username, password);

    if (username === "user" && password === "1234") {
        alert("Success");
        console.log("Yes");
      
    } else{
        console.log("No");
    }
});