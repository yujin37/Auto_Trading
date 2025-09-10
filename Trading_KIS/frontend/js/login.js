const loginForm = document.getElementById("login-form")
const loginButton = document.getElementById("login-form-submit")


loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const username = loginForm.username.value;
    const password = loginForm.password.value;

    console.log(username, password);

    const response = await fetch('http://127.0.0.1:5000/login', {  // Flask 기본 포트 5000
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    alert(data.message);
});