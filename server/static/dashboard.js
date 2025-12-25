let currentLead = null

async function loadLeads() {
    const res = await fetch('/api/leads')
    const leads = await res.json()
    const container = document.getElementById('leads')
    container.innerHTML = ''

    leads.forEach((lead) => {
        const div = document.createElement('div')
        div.className = 'lead'
        div.textContent = 'Lead #' + lead.id
        div.onclick = () => loadPreview(lead.id)
        container.appendChild(div)
    })

    if (leads.length === 0) {
        container.innerHTML = '<p>No pending leads</p>'
        document.getElementById('frame').src = ''
    }
}

function loadPreview(id) {
    currentLead = id
    document.getElementById('frame').src = '/preview/' + id
}

async function review(approved) {
    if (!currentLead) return

    await fetch('/review/' + currentLead, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved })
    })

    currentLead = null
    await loadLeads()
}

loadLeads()