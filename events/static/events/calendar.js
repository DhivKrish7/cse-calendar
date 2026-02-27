let calendar;
let selectedSymbol = "ALL";

document.addEventListener("DOMContentLoaded", function () {

    const calendarEl = document.getElementById("calendar_view");

    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth",
        height: "100%",
        headerToolbar: {
            left: "prev,next today",
            center: "title",
            right: "dayGridMonth,timeGridWeek"
        },
        events: fetchEvents,
        eventClick: handleEventClick,
        dateClick: handleDateClick,
        eventDidMount: styleEvent,

        datesSet: function() {
            fadeInCalendar();
        }
    });

    calendar.render();

    overrideNavButtons();
    openPanelsOnLoad();
    loadSymbols();
    loadSidePanels();
});

function fadeOutCalendar(callback) {
    const el = document.querySelector(".fc");
    el.classList.add("calendar-fade");

    setTimeout(() => {
        callback();
    }, 200);
}

function fadeInCalendar() {
    const el = document.querySelector(".fc");
    el.classList.remove("calendar-fade");
}

function overrideNavButtons() {

    document.querySelectorAll(".fc-prev-button, .fc-next-button, .fc-today-button")
        .forEach(btn => {
            btn.addEventListener("click", function(e){
                e.preventDefault();
                fadeOutCalendar(() => {
                    if (btn.classList.contains("fc-prev-button")) calendar.prev();
                    if (btn.classList.contains("fc-next-button")) calendar.next();
                    if (btn.classList.contains("fc-today-button")) calendar.today();
                });
            });
        });
}

// dateClick: function(info) {

//     const clickedDate = info.dateStr;

//     const events = calendar.getEvents().filter(ev => ev.startStr === clickedDate);

//     if (!events.length) {
//         document.getElementById("drawer-title").innerText = "No Events";
//         document.getElementById("drawer-content").innerHTML = "No events on this date.";
//     } else {

//         let html = "";

//         events.forEach(ev => {
//             const e = ev.extendedProps;

//             html += `
//                 <div class="drawer-event-block">
//                     <div><b>${ev.title}</b></div>
//                     <div>Symbol: ${e.symbol}</div>
//                     <div>Type: ${e.type}</div>
//                     <div>Date Type: ${e.date_type}</div>
//                     <hr>
//                 </div>
//             `;
//         });

//         document.getElementById("drawer-title").innerText = clickedDate;
//         document.getElementById("drawer-content").innerHTML = html;
//     }

//     document.getElementById("event-drawer").classList.add("open");
// }

function jumpToDate() {
    let year = document.getElementById("jump-year").value;
    let month = document.getElementById("jump-month").value;

    fadeOutCalendar(() => {
        calendar.gotoDate(`${year}-${month}-01`);
    });
}

let yearSelect = document.getElementById("jump-year");
for (let y = 2020; y <= 2035; y++) {
    let opt = document.createElement("option");
    opt.value = y;
    opt.text = y;
    yearSelect.appendChild(opt);
}

function closeDrawer() {
    document.getElementById("event-drawer").classList.remove("open");
}

function toggleSidebar() {
    document.querySelector(".sidebar-left").classList.toggle("collapsed");
    document.querySelector(".layout").classList.toggle("collapsed");

    setTimeout(() => {
        calendar.updateSize();
    }, 350);
}

const canvas = document.getElementById("bg-particles");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particles = [];

for (let i = 0; i < 40; i++) {
    particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * 2,
        speed: Math.random() * 0.3
    });
}

function fetchEvents(info, successCallback) {

    const type = document.getElementById("filter-type").value;

    let url = `/api/v1/events/?symbol=${selectedSymbol}&type=${type}&start=${info.startStr}&end=${info.endStr}`;

    fetch(url)
        .then(res => res.json())
        .then(data => {

            if (!data || !Array.isArray(data.data)) {
                successCallback([]);
                return;
            }

            successCallback(data.data);
            loadSidePanels(data.data);
        })
        .catch(err => {
            console.error("Event fetch error:", err);
            successCallback([]);
        });
}

function styleEvent(info) {
    const type = info.event.extendedProps.type;

    if (type === "DIVIDEND") info.el.classList.add("dividend");
    if (type === "RIGHTS ISSUE") info.el.classList.add("rights");
    if (type === "EARNINGS") info.el.classList.add("earnings");
    if (type === "BONUS ISSUE") info.el.classList.add("bonus");
    if (type === "SPLIT") info.el.classList.add("split");
}

function handleEventClick(info) {

    const e = info.event.extendedProps;

    document.getElementById("drawer-title").innerText = info.event.title;
    document.getElementById("drawer-content").innerHTML = `
        <div><b>Symbol:</b> ${e.symbol}</div>
        <div><b>Type:</b> ${e.type}</div>
        <div><b>Date Type:</b> ${e.date_type}</div>
    `;

    document.getElementById("event-drawer").classList.add("open");
}

function highlightDate(dateStr) {

    const cell = document.querySelector(`[data-date='${dateStr}']`);

    if (!cell) return;

    cell.classList.add("highlight-flash");
    // cell.classList.add("day-glow");

    setTimeout(() => {
        cell.classList.remove("highlight-flash");
    }, 3000);

    // setTimeout(() => {
    //     cell.classList.remove("day-glow");
    // }, 2500);
}

function loadSidePanels(events = null) {

    if (!events) {
        fetch(`/api/v1/events/?symbol=${selectedSymbol}&type=${document.getElementById("filter-type").value}`)
            .then(res => res.json())
            .then(data => {
                if (data && Array.isArray(data.data)) {
                    loadSidePanels(data.data);
                }
            });
        return;
    }
    if (!Array.isArray(events)) return;

    const today = new Date();
    const todayStr = today.getFullYear() + "-" +
        String(today.getMonth()+1).padStart(2,'0') + "-" +
        String(today.getDate()).padStart(2,'0');
    
    const todayEvents = events.filter(e => e.start === todayStr);
    const upcoming = events
        .filter(e => e.start > todayStr)
        .sort((a,b) => new Date(a.start) - new Date(b.start))
        .slice(0, 10);

    renderPanel("today-panel", todayEvents);
    renderPanel("upcoming-panel", upcoming);
}

function renderPanel(panelId, events) {

    const panel = document.getElementById(panelId);
    panel.innerHTML = "";

    events.forEach(ev => {
        const div = document.createElement("div");
        div.className = "upcoming-row";
        div.innerHTML = `
            <span>${ev.start}</span>
            <span>${ev.extendedProps.symbol}</span>
            <span>${ev.extendedProps.date_type}</span>
        `;

        div.onclick = () => {
            calendar.gotoDate(ev.start);
            highlightDate(ev.start);
        };

        panel.appendChild(div);
    });

    const parent = panel.parentElement.querySelector(".panel-body");
    if (parent.classList.contains("open")) {
        parent.style.maxHeight = parent.scrollHeight + "px";
    }
}

function togglePanel(id) {
    const panel = document.getElementById(id);

    if (panel.classList.contains("open")) {
        panel.style.maxHeight = panel.scrollHeight + "px";

        requestAnimationFrame(() => {
            panel.style.maxHeight = "0px";
        });

        panel.classList.remove("open");
    } else {
        panel.classList.add("open");
        panel.style.maxHeight = panel.scrollHeight + "px";
    }
}

function loadSymbols(query="") {

    const dropdown = document.getElementById("symbol-dropdown");

    if (!query) {
        dropdown.style.display = "none";
        return;
    }

    fetch(`/api/v1/symbols/?q=${query}`)
        .then(res => res.json())
        .then(symbols => {

            dropdown.innerHTML = "";

            if (!symbols.length) {
                dropdown.style.display = "none";
                return;
            }

            dropdown.style.display = "block";

            symbols.unshift("ALL");

            symbols.forEach(sym => {
                const div = document.createElement("div");
                div.innerText = sym;

                div.onclick = () => {
                    selectedSymbol = sym;
                    document.getElementById("symbol-search").value = sym;
                    dropdown.style.display = "none";
                    calendar.refetchEvents();
                };

                dropdown.appendChild(div);
            });
        });
}

document.getElementById("symbol-search")
.addEventListener("input", function () {
    const value = this.value.trim();
    loadSymbols(value);
});

document.addEventListener("click", function(e){
    if (!e.target.closest(".symbol-wrapper")) {
        document.getElementById("symbol-dropdown").style.display = "none";
    }
});

function handleDateClick(info) {

    const clickedDate = info.dateStr;

    const events = calendar.getEvents().filter(ev =>
        ev.startStr === clickedDate
    );

    let html = "";

    if (!events.length) {
        html = `<div>No events on this date.</div>`;
    } else {
        events.forEach(ev => {
            const e = ev.extendedProps;
            html += `
                <div class="drawer-event-block">
                    <div><b>${ev.title}</b></div>
                    <div>Symbol: ${e.symbol}</div>
                    <div>Type: ${e.type}</div>
                    <div>Date Type: ${e.date_type}</div>
                    <hr>
                </div>
            `;
        });
    }

    document.getElementById("drawer-title").innerText = clickedDate;
    document.getElementById("drawer-content").innerHTML = html;
    document.getElementById("event-drawer").classList.add("open");
}

function openPanelsOnLoad() {
    ["today-panel", "upcoming-panel"].forEach(id => {
        const panel = document.getElementById(id);
        panel.classList.add("open");
        panel.style.maxHeight = panel.scrollHeight + "px";
    });
}