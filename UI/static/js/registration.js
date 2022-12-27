    fetch("https://restcountries.com/v2/all")
        .then(res => res.json())
        .then(data => initialize(data))
        .catch(err => console.log(err));

    function initialize(data) {
        countries = data;
        let options = '';
        for (let i = 0; i < countries.length; i++) {
            console.log(countries[i]);
            options += `<option value="${countries[i].name}">${countries[i].name}</option>`;
        }
        console.log(options);
        document.getElementById('countries').innerHTML = options;

    }
    const container = document.querySelector(".container"),
        pwShowHide = document.querySelectorAll(".showHidePw"),
        pwFields = document.querySelectorAll(".password"),
        signUp = document.querySelector(".signup-link"),
        login = document.querySelector(".login-link");

    //   js code to show/hide password and change icon
    pwShowHide.forEach(eyeIcon => {
        eyeIcon.addEventListener("click", () => {
            pwFields.forEach(pwField => {
                if (pwField.type === "password") {
                    pwField.type = "text";

                    pwShowHide.forEach(icon => {
                        icon.classList.replace("uil-eye-slash", "uil-eye");
                    })
                } else {
                    pwField.type = "password";

                    pwShowHide.forEach(icon => {
                        icon.classList.replace("uil-eye", "uil-eye-slash");
                    })
                }
            })
        })
    })

    // js code to appear signup and login form
    signUp.addEventListener("click", () => {
        container.classList.add("active");
    });
    login.addEventListener("click", () => {
        container.classList.remove("active");
    });