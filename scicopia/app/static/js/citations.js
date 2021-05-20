function citations(key, sigma) {
  let xhr = new XMLHttpRequest();
  xhr.open("POST", "/citations", true);
    xhr.responseType = "json";
    xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');

    xhr.onload = function() {
        let json = xhr.response;
        if (typeof json === "undefined") {
        console.log('Citation key response empty.');
        return {};
        }
        sigma.graph.clear();
        sigma.graph.read(json);
        sigma.refresh();
    } 
    xhr.send("key=" + key);
}