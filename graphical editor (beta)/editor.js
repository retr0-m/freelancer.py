const TA_CLASS = "__inspector_textarea_xyz123";
var edits = {};

function addGeneralEditButtons() {
    generalEdits = document.createElement("input");
    generalEdits.style.padding = "10px";
    generalEdits.style.width = "70%";
    generalEdits.style.display = "inline-block"

    title = document.createElement("p")
    title.style.color = "white"
    title.textContent = "General Edits"


    confirm = document.createElement("button")
    confirm.textContent = "Apply edits"
    confirm.style.padding = "10px"
    confirm.style.width = "25%"
    confirm.style.float = "right"
    confirm.onclick = send_data_to_py_backend

    container = document.createElement("div")
    container.appendChild(title)
    container.appendChild(generalEdits)
    container.appendChild(confirm)
    container.style.position = "absolute"
    container.style.top = "150px"
    container.style.zIndex = "2000"
    container.style.width = "40vw"
    container.classList.add(TA_CLASS)
    container.style.background = "rgba(24,24,24,0.8)"
    container.style.padding = "10px"
    container.style.borderRadius = "20px"

    document.body.appendChild(container)
}


document.addEventListener("click", (e) => {
    // Ignore clicks inside our own textboxes
    if (e.target.closest("." + TA_CLASS)) return;
    e.target.style.border = "2px solid orange"
    e.preventDefault();
    e.stopPropagation();

    const el = e.target;
    const rect = el.getBoundingClientRect();

    // Container (so buttons can sit inside)
    const box = document.createElement("div");
    box.className = TA_CLASS;
    box.style.position = "absolute";
    box.style.left = (rect.left + window.scrollX) + "px";
    box.style.top = (rect.bottom + window.scrollY + 4) + "px";
    box.style.padding = "4px";
    box.style.background = "white";
    box.style.border = "1px solid black";
    box.style.borderRadius = "5px";
    box.style.zIndex = 999999;
    box.style.display = "flex";
    box.style.alignItems = "center";
    box.style.gap = "4px";

    // Small textarea
    const ta = document.createElement("textarea");
    ta.style.width = "120px";
    ta.style.height = "40px";
    ta.style.resize = "none";
    ta.style.outline = "none";

    // "+" confirm button
    const btnAdd = document.createElement("button");
    btnAdd.textContent = "+";
    btnAdd.style.padding = "2px 6px";
    btnAdd.style.cursor = "pointer";
    btnAdd.onclick = () => {
        if (ta.value.replaceAll(" ", "") != "") {
            edits[getUniqueSelector(el)] = ta.value;
            console.log(edits)
            ta.style.border = "none"
            ta.style.background = "transparent"
            ta.style.textAlign = "center"
            btnAdd.style.display = "none"
            btnDel.style.display = "none"
        }
    };

    // "x" delete button
    const btnDel = document.createElement("button");
    btnDel.textContent = "x";
    btnDel.style.padding = "2px 6px";
    btnDel.style.cursor = "pointer";
    btnDel.onclick = () => {
        box.remove();
    };

    // Assemble
    box.appendChild(ta);
    box.appendChild(btnAdd);
    box.appendChild(btnDel);
    document.body.appendChild(box);

    ta.focus();
});




let last;
document.addEventListener("mousemove", (e) => {
    const el = document.elementFromPoint(e.clientX, e.clientY);

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
    const data = edits;

    fetch("http://localhost:8000/receive", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
}



addGeneralEditButtons()