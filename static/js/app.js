let participantsCache = [];
document.addEventListener('DOMContentLoaded', () => {
    loadParticipants();
    document.getElementById('participantForm').addEventListener('submit', handleParticipantSubmit);
    document.getElementById('abstractForm').addEventListener('submit', handleAbstractSubmit);
    document.getElementById('invitationForm').addEventListener('submit', handleInvitationSubmit);
    document.getElementById('feeForm').addEventListener('submit', handleFeeSubmit);
    document.getElementById('hotelForm').addEventListener('submit', handleHotelSubmit);
});

function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    event.target.classList.add('active');
    if (tabId === 'abstracts') loadAbstracts();
    if (tabId === 'invitations') loadInvitations();
    if (tabId === 'org') { loadFees(); loadHotels(); }
}

function showMessage(id, text, isSuccess) {
    const el = document.getElementById(id);
    el.textContent = text;
    el.className = `message ${isSuccess ? 'success' : 'error'}`;
    setTimeout(() => { el.className = 'message'; }, 4000);
}

function updateSelects() {
    ['a_participant_id', 'i_participant_id', 'f_participant_id', 'h_participant_id'].forEach(id => {
        const sel = document.getElementById(id);
        if(sel) sel.innerHTML = '<option value="">Выберите...</option>' + participantsCache.map(p => `<option value="${p.id}">${p.full_name} (${p.role})</option>`).join('');
    });
}

async function loadParticipants() {
    const res = await fetch('/participants/');
    participantsCache = await res.json();
    updateSelects();
    document.getElementById('participantsList').innerHTML = participantsCache.map(p => 
        `<div class="data-card"><div><strong>${p.full_name}</strong><br><small>${p.email} | ${p.role}</small></div><button class="btn-delete" onclick="del('/participants/${p.id}', loadParticipants)">Удалить</button></div>`
    ).join('') || '<p>Нет участников</p>';
}

async function handleParticipantSubmit(e) {
    e.preventDefault();
    const data = { full_name: p_full_name.value, email: p_email.value, role: p_role.value, is_online: p_is_online.checked };
    const res = await fetch('/participants/', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
    if(res.ok) { showMessage('p_message', 'Успех', true); e.target.reset(); loadParticipants(); }
    else showMessage('p_message', 'Ошибка: ' + (await res.json()).detail, false);
}

async function handleAbstractSubmit(e) {
    e.preventDefault();
    const data = { participant_id: parseInt(a_participant_id.value), title: a_title.value, content: a_content.value };
    const res = await fetch('/science/abstracts/', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
    if(res.ok) { showMessage('a_message', 'Успех', true); e.target.reset(); loadAbstracts(); }
    else showMessage('a_message', 'Ошибка: ' + (await res.json()).detail, false);
}

async function handleInvitationSubmit(e) {
    e.preventDefault();
    const data = { participant_id: parseInt(i_participant_id.value), text: i_text.value };
    const res = await fetch('/science/invitations/', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
    if(res.ok) { showMessage('i_message', 'Успех', true); e.target.reset(); loadInvitations(); }
    else showMessage('i_message', 'Ошибка: ' + (await res.json()).detail, false);
}

async function handleFeeSubmit(e) {
    e.preventDefault();
    const data = { participant_id: parseInt(f_participant_id.value), amount: parseFloat(f_amount.value) };
    const res = await fetch('/org/fees/', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
    if(res.ok) { showMessage('f_message', 'Успех', true); e.target.reset(); loadFees(); }
    else showMessage('f_message', 'Ошибка: ' + (await res.json()).detail, false);
}

async function handleHotelSubmit(e) {
    e.preventDefault();
    const data = { participant_id: parseInt(h_participant_id.value), check_in: h_check_in.value, check_out: h_check_out.value };
    const res = await fetch('/org/hotels/', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
    if(res.ok) { showMessage('h_message', 'Успех', true); e.target.reset(); loadHotels(); }
    else showMessage('h_message', 'Ошибка: ' + (await res.json()).detail, false);
}

async function loadAbstracts() {
    const res = await fetch('/science/abstracts/');
    const data = await res.json();
    document.getElementById('abstractsList').innerHTML = data.map(a => `<div class="data-card"><div><strong>${a.title}</strong><br><small>ID: ${a.participant_id}</small></div><button class="btn-delete" onclick="del('/science/abstracts/${a.id}', loadAbstracts)">Удалить</button></div>`).join('') || '<p>Нет тезисов</p>';
}

async function loadInvitations() {
    const res = await fetch('/science/invitations/');
    const data = await res.json();
    document.getElementById('invitationsList').innerHTML = data.map(i => `<div class="data-card"><div><strong>Для ID: ${i.participant_id}</strong><br><small>${i.text}</small></div><button class="btn-delete" onclick="del('/science/invitations/${i.id}', loadInvitations)">Удалить</button></div>`).join('') || '<p>Нет приглашений</p>';
}

async function loadFees() {
    const res = await fetch('/org/fees/');
    const data = await res.json();
    document.getElementById('feesList').innerHTML = data.map(f => `<div class="data-card"><div><strong>ID: ${f.participant_id} | ${f.amount}₽</strong><br><small style="color:${f.status==='paid'?'green':'red'}">${f.status==='paid'?'Оплачен':'Не оплачен'}</small></div><div>${f.status!=='paid'?`<button class="btn-secondary" onclick="pay(${f.id})">Оплатить</button>`:''} <button class="btn-delete" onclick="del('/org/fees/${f.id}', loadFees)">Удалить</button></div></div>`).join('') || '<p>Нет взносов</p>';
}

async function loadHotels() {
    const res = await fetch('/org/hotels/');
    const data = await res.json();
    document.getElementById('hotelsList').innerHTML = data.map(h => `<div class="data-card"><div><strong>ID: ${h.participant_id} | ${h.check_in} - ${h.check_out}</strong><br><small>${h.status==='booked'?'Забронировано':'Ожидает'}</small></div><div>${h.status!=='booked'?`<button class="btn-secondary" onclick="book(${h.id})">Забронировать</button>`:''} <button class="btn-delete" onclick="del('/org/hotels/${h.id}', loadHotels)">Удалить</button></div></div>`).join('') || '<p>Нет заявок</p>';
}

async function pay(id) {
    const res = await fetch(`/org/fees/${id}/pay`, { method: 'PATCH' });
    if(res.ok) loadFees(); else alert('Ошибка');
}

async function book(id) {
    const res = await fetch(`/org/hotels/${id}/book`, { method: 'PATCH' });
    if(res.ok) loadHotels(); else { const err = await res.json(); showMessage('h_message', 'Ошибка: ' + err.detail, false); }
}

async function del(url, reload) {
    if(!confirm('Удалить?')) return;
    const res = await fetch(url, { method: 'DELETE' });
    if(res.ok || res.status === 204) reload(); else alert('Ошибка удаления');
}