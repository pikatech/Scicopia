function total() {
  let xhr = new XMLHttpRequest();
  xhr.open("GET", "/total");
  xhr.responseType = "json";

  xhr.onload = function() {
    let elem = document.getElementById("hitstats");
    let json = xhr.response;
    let totalhits = document.createElement('p');
    totalhits.textContent = json['total'];
    elem.appendChild(totalhits);
  }

  xhr.send("");
}
