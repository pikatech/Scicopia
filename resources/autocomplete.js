// eslint-disable-next-line no-unused-vars
function autocomplete(inp) {
  /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/
  let currentFocus;
  /*execute a function when someone writes in the text field:*/
  inp.addEventListener("input", function() {
      query_es(this);
  });
  /*execute a function presses a key on the keyboard:*/
  inp.addEventListener("keydown", function(e) {
      let x = document.getElementById(this.id + "-autocomplete-list");
      if (x) x = x.getElementsByTagName("div");
      if (e.keyCode == 40) {
        /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
        currentFocus++;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 38) { //up
        /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
        currentFocus--;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 13) {
        /*If the ENTER key is pressed, prevent the form from being submitted,*/
        if (currentFocus > -1) {
          e.preventDefault();
          /*and simulate a click on the "active" item:*/
          if (x) x[currentFocus].click();
          currentFocus = -1;
        }
      }
  });
  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
  }
  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (let i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }
  function closeAllLists(elmnt) {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
    let x = document.getElementsByClassName("autocomplete-items");
    for (let i = 0; i < x.length; i++) {
      if (elmnt != x[i] && elmnt != inp) {
        x[i].parentNode.removeChild(x[i]);
      }
    }
  }
  /*execute a function when someone clicks in the document:*/
  document.addEventListener("click", function (e) {
      closeAllLists(e.target);
  });
  function query_es(elem) {
    let user_input = elem.value;
    // Empty string
    if (!user_input) {
      return;
    }

    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/autocomplete", true);
    xhr.responseType = "json";
    xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
  
    xhr.onload = function() {
      let json = xhr.response;
      if (typeof json === "undefined") {
        console.log('Auto-completion response empty.');
        return;
      }
      let suggestions = json['completions'];
      if (typeof suggestions === "undefined") {
        console.log('There were no sugggestions.');
        return;
      }
      let prefix = json['prefix'];
      let term = json['term'];

      let a, b, i;
      /*close any already open lists of autocompleted values*/
      closeAllLists();
      if (!term) {return false;}
      currentFocus = -1;
      /*create a DIV element that will contain the items (values):*/
      a = document.createElement("DIV");
      a.setAttribute("id", elem.id + "-autocomplete-list");
      a.setAttribute("class", "autocomplete-items");
      /*append the DIV element as a child of the autocomplete container:*/
      elem.parentNode.appendChild(a);
      /*for each item in the array...*/
      for (i = 0; i < suggestions.length; i++) {
        /*create a DIV element for each matching element:*/
        b = document.createElement("DIV");
        /*check if the item starts with the same letters as the text field value:*/
        if (suggestions[i].substr(0, term.length).toUpperCase() == term.toUpperCase()) {
          /*make the matching letters bold:*/
          b.innerHTML = prefix + "<strong>" + suggestions[i].substr(0, term.length) + "</strong>";
          b.innerHTML += suggestions[i].substr(term.length);
        } else {
          b.innerHTML = prefix + suggestions[i];
        }
        /*insert a input field that will hold the current array item's value:*/
        b.innerHTML += "<input type='hidden' value='" + prefix + suggestions[i] + "'>";
        /*execute a function when someone clicks on the item value (DIV element):*/
        b.addEventListener("click", function() {
            /*insert the value for the autocomplete text field:*/
            elem.value = this.getElementsByTagName("input")[0].value;
            /*close the list of autocompleted values,
            (or any other open lists of autocompleted values:*/
            closeAllLists();
        });
        a.appendChild(b);
      }
      return suggestions;
    } 
    xhr.send("prefix=" + user_input);
  }
}