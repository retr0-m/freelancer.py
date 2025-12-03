const TA_CLASS = "__inspector_textarea_xyz123";
const GEN_EDITS_ID = "__general_edits_input_inspector__"
var edits = {};

// disable seleciton
document.body.addEventListener("mousedown", (e) => {
    if (!e.target.closest("input, textarea")) {
        e.preventDefault();
    }
});

document.body.addEventListener("selectstart", (e) => {
    if (!e.target.closest("input, textarea")) {
        e.preventDefault();
    }
});


function addGeneralEditButtons() {
    // --- Textarea ---
    let generalEdits = document.createElement("textarea");
    generalEdits.style.padding = "12px";
    generalEdits.style.width = "100%";
    generalEdits.style.height = "120px";
    generalEdits.style.display = "block";
    generalEdits.style.marginTop = "10px";
    generalEdits.style.fontSize = "14px";
    generalEdits.style.borderRadius = "10px";
    generalEdits.style.border = "none";
    generalEdits.style.outline = "none";
    generalEdits.style.resize = "vertical";
    generalEdits.style.background = "rgba(255,255,255,0.05)";
    generalEdits.style.color = "white";
    generalEdits.id = GEN_EDITS_ID;

    // --- Title ---
    let title = document.createElement("p");
    title.style.color = "white";
    title.style.margin = "0";
    title.style.fontWeight = "bold";
    title.textContent = "Generic edits";

    // --- Button ---
    let confirm = document.createElement("button");
    confirm.textContent = "→";
    confirm.style.border = "0";
    confirm.style.height = "60px";
    confirm.style.width = "60px";
    confirm.style.borderRadius = "50%";
    confirm.style.marginTop = "10px";
    confirm.style.float = "right";
    confirm.style.backdropFilter = "blur(6px)";
    confirm.style.background = "linear-gradient(180deg, rgba(2, 6, 23, 0.55), rgba(2, 6, 23, 0.35))";
    confirm.style.color = "white";
    confirm.style.fontSize = "20px";
    confirm.style.cursor = "pointer";
    confirm.style.transition = "all 0.2s ease";
    confirm.style.boxShadow = "0 4px 8px rgba(0,0,0,0.3)";

    // Hover effect
    confirm.addEventListener("mouseenter", () => {
        confirm.style.transform = "scale(1.1)";
        confirm.style.boxShadow = "0 6px 12px rgba(0,0,0,0.5)";
    });
    confirm.addEventListener("mouseleave", () => {
        confirm.style.transform = "scale(1)";
        confirm.style.boxShadow = "0 4px 8px rgba(0,0,0,0.3)";
    });

    // Press effect
    confirm.addEventListener("mousedown", () => {
        confirm.style.transform = "scale(0.95)";
        confirm.style.boxShadow = "0 2px 4px rgba(0,0,0,0.2)";
    });
    confirm.addEventListener("mouseup", () => {
        confirm.style.transform = "scale(1.1)";
        confirm.style.boxShadow = "0 6px 12px rgba(0,0,0,0.5)";
    });

    confirm.onclick = function () {
        send_data_to_py_backend()
        showLoadingOverlay()
    };

    // --- Container ---
    let container = document.createElement("div");
    container.appendChild(title);
    container.appendChild(generalEdits);
    container.appendChild(confirm);
    container.style.position = "fixed";
    container.style.top = "150px";
    container.style.zIndex = "2000";
    container.style.width = "400px";
    container.classList.add(TA_CLASS);
    container.style.background = "linear-gradient(180deg, rgba(2, 6, 23, 0.55), rgba(2, 6, 23, 0.35))";
    container.style.padding = "15px";
    container.style.borderRadius = "20px";
    container.style.backdropFilter = "blur(6px)";
    container.style.boxShadow = "0 8px 20px rgba(0,0,0,0.5)";

    document.body.appendChild(container);
    makeDraggable(container); // make it draggable
    container.style.cursor = "grab"; // initial cursor style
}

function makeDraggable(element) {
    let isDragging = false;
    let offsetX = 0;
    let offsetY = 0;

    element.addEventListener("mousedown", (e) => {
        isDragging = true;
        // Calculate offset between mouse and top-left corner of the element
        offsetX = e.clientX - element.getBoundingClientRect().left;
        offsetY = e.clientY - element.getBoundingClientRect().top;
        element.style.cursor = "grabbing";
    });

    document.addEventListener("mousemove", (e) => {
        if (isDragging) {
            element.style.left = e.clientX - offsetX + "px";
            element.style.top = e.clientY - offsetY + "px";
        }
    });

    document.addEventListener("mouseup", () => {
        isDragging = false;
        element.style.cursor = "grab";
    });
}

document.addEventListener("click", (e) => {
    // Ignore clicks inside our own boxes
    if (e.target.closest("." + TA_CLASS)) return;

    const el = e.target;
    const rect = el.getBoundingClientRect();

    // Highlight selected element
    el.style.outline = "2px solid orange";

    // --- Container ---
    const box = document.createElement("div");
    box.className = TA_CLASS;
    box.style.position = "absolute";
    box.style.left = (rect.left + window.scrollX) + "px";
    box.style.top = (rect.bottom + window.scrollY + 6) + "px";
    box.style.padding = "6px";
    box.style.background = "rgba(20,20,20,0.95)";
    box.style.border = "1px solid rgba(255,255,255,0.2)";
    box.style.borderRadius = "10px";
    box.style.boxShadow = "0 4px 12px rgba(0,0,0,0.4)";
    box.style.zIndex = 999999;
    box.style.display = "flex";
    box.style.alignItems = "center";
    box.style.gap = "6px";
    box.style.backdropFilter = "blur(6px)";
    box.style.color = "white";
    box.style.fontFamily = "sans-serif";

    // --- Textarea ---
    const ta = document.createElement("textarea");
    ta.style.width = "140px";
    ta.style.height = "50px";
    ta.style.resize = "vertical";
    ta.style.outline = "none";
    ta.style.border = "1px solid rgba(255,255,255,0.3)";
    ta.style.borderRadius = "6px";
    ta.style.padding = "4px";
    ta.style.background = "rgba(0,0,0,0.2)";
    ta.style.color = "white";
    ta.style.fontSize = "13px";

    // --- "+" Confirm Button ---
    const btnAdd = document.createElement("button");
    btnAdd.textContent = "+";
    btnAdd.style.padding = "4px 8px";
    btnAdd.style.cursor = "pointer";
    btnAdd.style.border = "none";
    btnAdd.style.borderRadius = "6px";
    btnAdd.style.background = "linear-gradient(180deg, #2a6, #1a4)";
    btnAdd.style.color = "white";
    btnAdd.style.fontWeight = "bold";
    btnAdd.style.transition = "all 0.2s ease";

    btnAdd.addEventListener("mouseenter", () => {
        btnAdd.style.transform = "scale(1.1)";
        btnAdd.style.filter = "brightness(1.2)";
    });
    btnAdd.addEventListener("mouseleave", () => {
        btnAdd.style.transform = "scale(1)";
        btnAdd.style.filter = "brightness(1)";
    });
    btnAdd.addEventListener("mousedown", () => {
        btnAdd.style.transform = "scale(0.95)";
    });
    btnAdd.addEventListener("mouseup", () => {
        btnAdd.style.transform = "scale(1.1)";
    });

    btnAdd.onclick = () => {
        if (ta.value.replaceAll(" ", "") != "") {
            edits[getUniqueSelector(el)] = ta.value;
            console.log(edits);

            // Make the textarea read-only / not editable
            ta.readOnly = true;

            // Optional: style to show it’s disabled
            ta.style.background = "rgba(255,255,255,0.05)";
            ta.style.border = "none";
            ta.style.color = "gray";

            // Hide buttons
            btnAdd.style.display = "none";
            btnDel.style.display = "none";
        }
    };

    // --- "x" Delete Button ---
    const btnDel = document.createElement("button");
    btnDel.textContent = "x";
    btnDel.style.padding = "4px 8px";
    btnDel.style.cursor = "pointer";
    btnDel.style.border = "none";
    btnDel.style.borderRadius = "6px";
    btnDel.style.background = "linear-gradient(180deg, #a22, #811)";
    btnDel.style.color = "white";
    btnDel.style.fontWeight = "bold";
    btnDel.style.transition = "all 0.2s ease";

    btnDel.addEventListener("mouseenter", () => {
        btnDel.style.transform = "scale(1.1)";
        btnDel.style.filter = "brightness(1.2)";
    });
    btnDel.addEventListener("mouseleave", () => {
        btnDel.style.transform = "scale(1)";
        btnDel.style.filter = "brightness(1)";
    });
    btnDel.addEventListener("mousedown", () => {
        btnDel.style.transform = "scale(0.95)";
    });
    btnDel.addEventListener("mouseup", () => {
        btnDel.style.transform = "scale(1.1)";
    });

    btnDel.onclick = () => {
        el.style.outline = "none";
        box.remove();
    };

    // --- Assemble ---
    box.appendChild(ta);
    box.appendChild(btnAdd);
    box.appendChild(btnDel);
    document.body.appendChild(box);

    ta.focus();
});



let last;
document.addEventListener("mousemove", (e) => {
    const el = document.elementFromPoint(e.clientX, e.clientY);
    el.style.transition = "0.2s"

    // Do not highlight if hovering inside our inspector UI
    if (el && el.closest(".__inspector_textarea_xyz123")) {
        if (last) last.style.outline = "";
        last = null;
        return;
    }

    if (last) last.style.outline = ""; // remove old outline

    if (el) {
        el.style.outline = "2px solid red";
        last = el;
    }
});




function getUniqueSelector(el) {
    if (!(el instanceof Element)) return null;

    // 1. If element has an ID → use it
    if (el.id) {
        return `#${CSS.escape(el.id)}`;
    }

    // 2. Try to use unique class
    if (el.classList.length > 0) {
        const classes = [...el.classList].map(c => `.${CSS.escape(c)}`).join("");
        const selector = el.tagName.toLowerCase() + classes;

        // Check if this selector is unique
        if (document.querySelectorAll(selector).length === 1) {
            return selector;
        }
    }

    // 3. Use nth-child
    let path = [];
    let current = el;

    while (current && current.nodeType === Node.ELEMENT_NODE) {

        let selector = current.tagName.toLowerCase();

        // Add classes if available
        if (current.classList.length > 0) {
            selector += [...current.classList].map(c => `.${CSS.escape(c)}`).join("");
        }

        // Add nth-child because ID/class isn't enough
        const parent = current.parentNode;
        if (parent) {
            const index = [...parent.children].indexOf(current) + 1;
            selector += `:nth-child(${index})`;
        }

        path.unshift(selector);

        // Stop early if this path is already unique
        const full = path.join(" > ");
        if (document.querySelectorAll(full).length === 1) {
            return full;
        }

        current = parent;
    }

    // Last fallback → full path
    return path.join(" > ");
}

function send_data_to_py_backend() {
    gen_edits = document.querySelector("#" + GEN_EDITS_ID)
    console.log(gen_edits.value)
    if (gen_edits.value.replace(" ", "") != "") {
        edits["generic"] = gen_edits.value;
    }
    const data = edits;

    fetch("http://localhost:8000/receive", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
}


function showLoadingOverlay() {
    // --- Overlay ---
    const overlay = document.createElement("div");
    overlay.id = "loadingOverlay";
    overlay.style.position = "fixed";
    overlay.style.top = 0;
    overlay.style.left = 0;
    overlay.style.width = "100%";
    overlay.style.height = "100%";
    overlay.style.backdropFilter = "blur(6px)";
    overlay.style.background = "rgba(0,0,0,0.3)";
    overlay.style.zIndex = 999999;
    overlay.style.display = "flex";
    overlay.style.alignItems = "center";
    overlay.style.justifyContent = "center";


    // --- Futuristic AI Loader ---
    const loader = document.createElement("div");
    loader.style.width = "80px";
    loader.style.height = "80px";
    loader.style.border = "4px solid rgba(141, 181, 181, 0.2)";
    loader.style.borderTop = "4px solid rgb(255,255,230)";
    loader.style.borderRadius = "50%";
    loader.style.animation = "spin 1s linear infinite";
    loader.style.boxShadow = "0 0 15px grey, 0 0 30px rgba(71, 86, 86, 0.3) inset";

    overlay.appendChild(loader);
    document.body.appendChild(overlay);

    // --- Add animation style dynamically ---
    const style = document.createElement("style");
    style.innerHTML = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);

    // --- Optional: Return a function to remove overlay ---
    return () => {
        document.body.removeChild(overlay);
    };
}

let lastContent = null;

async function checkUpdate() {
    try {
        const response = await fetch(window.location.href + "?_=" + new Date().getTime(), {
            cache: "no-store"
        });
        const text = await response.text();

        if (lastContent && text !== lastContent) {
            window.location.reload();
        }
        lastContent = text;
    } catch (err) {
        console.error("Error checking page update:", err);
    }
}

// Check every 2 seconds
setInterval(checkUpdate, 2000);

addGeneralEditButtons()