document.addEventListener("DOMContentLoaded", function(){
    function toggleInlines(){
        let eventTypeField = document.querySelector("#id_event_type");
        if (!eventTypeField) return;

        let value = eventTypeField.value;

        let dividend = document.querySelector(".inline-group[id*='dividend']");
        let rights = document.querySelector(".inline-group[id*='rights']");
        let bonus = document.querySelector(".inline-group[id*='bonus']");
        let split = document.querySelector(".inline-group[id*='split']");
        let earnings = document.querySelector(".inline-group[id*='earnings']");

        [dividend, rights, split, bonus, earnings].forEach(el =>{
            if (el) el.style.display = "none";
        });

        if (value === "DIVIDEND" && dividend) dividend.style.display = "block";
        if (value === "SPLIT" && split) split.style.display = "block";
        if (value === "BONUS ISSUE" && bonus) bonus.style.display = "block";
        if (value === "RIGHTS ISSUE" && rights) rights.style.display = "block";
        if (value === "EARNINGS" && earnings) earnings.style.display = "block";
    }
    toggleInlines();

    document.addEventListener("change", function(e){
        if (e.target.id === "id_event_type"){
            toggleInlines();
        }
    });
});