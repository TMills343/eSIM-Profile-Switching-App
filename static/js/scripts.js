/**

Handles the file select event and updates the form fields accordingly.
@param {Event} event - The file select event.
*/
function handleFileSelect(event) {
    var file = event.target.files[0];
    if (file) {
        document.getElementById("beginTest").removeAttribute("disabled");
        document.getElementById("eid").setAttribute("disabled", true);
        document.getElementById("imei").setAttribute("disabled", true);
        document.getElementById("bs_iccid").setAttribute("disabled", true);
    } else {
        document.getElementById("beginTest").setAttribute("disabled", true);
        document.getElementById("eid").removeAttribute("disabled");
        document.getElementById("imei").removeAttribute("disabled");
        document.getElementById("bs_iccid").removeAttribute("disabled");
    }
}

/**
 * This script is triggered when the document is fully loaded. It attaches 'click' event listeners
 * to each tab in the navigation bar.
 *
 * @listens DOMContentLoaded
 */
document.addEventListener('DOMContentLoaded', function() {

    var tabs = document.querySelectorAll('nav ul li');

    tabs.forEach(function(tab) {
        tab.addEventListener('click', function() {

            tabs.forEach(function(innerTab) {
                innerTab.classList.remove('active');
            });

            tab.classList.add('active');
        });
    });
});
