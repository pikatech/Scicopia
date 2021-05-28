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
        console.log(json)
        sigma.graph.clear();
        sigma.graph.read(json);
        sigma.graph.nodes().forEach(function(n) {
          n.originalColor = n.color;
        });
        sigma.graph.edges().forEach(function(e) {
          e.originalColor = e.color;
        });
        sigma.camera.goTo({
          x: 0,
          y: 0,
          angle: 0,
          ratio: 1
        });
        sigma.refresh();
    } 
    xhr.send("key=" + key);
}