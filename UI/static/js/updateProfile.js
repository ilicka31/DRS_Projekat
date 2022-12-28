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

function passwordChange(password) {
    passwordChangeForm = '<input type>';

}