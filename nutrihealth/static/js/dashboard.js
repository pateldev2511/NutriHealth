// Append close to each list item
// var myNodelist = document.getElementsByTagName("li");
// var i;
// for (i = 1; i < myNodelist.length; i++) {
//     var span = document.createElement("span");
//     var txt = document.createTextNode("\u00D7");
//     span.className = "close";
//     span.appendChild(txt);
//     myNodelist[i].appendChild(span);
// }

// List item delete
function removeMealHandler() {
    var meal_history_id = event.target.id;
    if (meal_history_id === '') {
        return;
    }
    location.href = '/recipe/remove_history/?meal_history_id=' + meal_history_id;
}

function removeExerciseHandler() {
    var exercise_history_id = event.target.id;
    if (exercise_history_id === '') {
        return;
    }
    location.href = '/exercise/remove_history/?exercise_history_id=' + exercise_history_id;
}

function addWaterIntake() {

    var waterintake = document.getElementById("txtWaterIntake").value;
    // if (waterintake.trim() != "" || waterintake.trim() != 0) {
    //     $.ajax({
    //         url: "/dashboard/addwater/?waterintake=" + waterintake,
    //         contentType: "application/json; charset=utf-8",
    //         dataType: "json",
    //         success: function (data) {
    //             alert(data.message);
    //             document.getElementById("txtWaterIntake").value = "";
    //         },
    //         error(errorData) {
    //             alert(errorData.statusText);
    //             window.location.reload();
    //         }
    //     });
    // } else {
    //     alert("please enter water intake amount");
    // }
    location.href = '/dashboard/addwater/?waterintake=' + waterintake;
}


// Add breakfast item
function newBreakfast() {
    var li = document.createElement("li");
    var userInput = document.getElementById("myInput").value;
    var newText = document.createTextNode(userInput);
    li.appendChild(newText);
    if (userInput === '') {
        alert("No input.");
    } else {
        document.getElementById("breakfast_list").appendChild(li);
    }
    document.getElementById("myInput").value = "";

    var span = document.createElement("span");
    var txt = document.createTextNode("\u00D7");
    span.className = "close";
    span.appendChild(txt);
    li.appendChild(span);

    for (i = 0; i < close.length; i++) {
        close[i].onclick = function () {
            var div = this.parentElement;
            div.style.display = "none";
        }
    }
}

// Add lunch item
function newLunch() {
    var li = document.createElement("li");
    var userInput = document.getElementById("myInput").value;
    var newText = document.createTextNode(userInput);
    li.appendChild(newText);
    if (userInput === '') {
        alert("No input.");
    } else {
        document.getElementById("lunch_list").appendChild(li);
    }
    document.getElementById("myInput").value = "";

    var span = document.createElement("span");
    var txt = document.createTextNode("\u00D7");
    span.className = "close";
    span.appendChild(txt);
    li.appendChild(span);

    for (i = 0; i < close.length; i++) {
        close[i].onclick = function () {
            var div = this.parentElement;
            div.style.display = "none";
        }
    }
}

// Add dinner item
function newDinner() {
    var li = document.createElement("li");
    var userInput = document.getElementById("myInput").value;
    var newText = document.createTextNode(userInput);
    li.appendChild(newText);
    if (userInput === '') {
        alert("No input.");
    } else {
        document.getElementById("dinner_list").appendChild(li);
    }
    document.getElementById("myInput").value = "";

    var span = document.createElement("span");
    var txt = document.createTextNode("\u00D7");
    span.className = "close";
    span.appendChild(txt);
    li.appendChild(span);

    for (i = 0; i < close.length; i++) {
        close[i].onclick = function () {
            var div = this.parentElement;
            div.style.display = "none";
        }
    }
}   