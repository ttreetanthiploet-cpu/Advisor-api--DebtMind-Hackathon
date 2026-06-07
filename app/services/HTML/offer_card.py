"""
offer_card.py — single HTML template for all plan types.
icon_url hardcoded. Single injection point: __OFFER_DATA__
"""

_ICON = "https://cdn-icons-png.flaticon.com/512/3135/3135706.png"

OFFER_CARD = r"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>OFFER CARD</title>
<style>
*{box-sizing:border-box}
body{margin:0;padding:16px;font-family:Arial,sans-serif;background:#eaf2fb;display:flex;justify-content:center}
.container{width:100%;max-width:420px}
.card{width:100%;background:#fff;border-radius:16px;padding:12px;border:1px solid rgba(47,128,237,.10);box-shadow:0 4px 12px rgba(0,0,0,.06);overflow:hidden}
.hidden{display:none!important}
.header{display:flex;align-items:flex-start;gap:10px;margin-bottom:8px}
.icon{width:36px;height:36px;background:#e8f1ff;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.icon img{width:18px;height:18px}
.title-wrap{flex:1;min-width:0}
.plan-id{display:block;color:#9ca3af;font-size:10px;font-weight:700;margin-bottom:2px}
.title{font-size:12px;line-height:1.4;color:#111827;font-weight:700;word-break:break-word}
.badge{display:inline-block;margin-top:5px;padding:3px 7px;border-radius:999px;background:#fff4e5;color:#b45309;font-size:9px;font-weight:700}
.account-bar{margin-top:8px;padding:8px 10px;background:#f8fbff;border:1px solid #dbeafe;border-radius:10px}
.account-label{font-size:10px;color:#6b7280;margin-bottom:2px}
.account-value{font-size:12px;color:#111827;font-weight:700;word-break:break-word}
.highlight-box{background:#edf5ff;border-radius:14px;padding:12px;text-align:center;margin:12px 0}
.before-after{font-size:11px;color:#6b7280;margin-bottom:6px}
.price{display:flex;justify-content:center;align-items:center;flex-wrap:wrap;gap:6px}
.old-price{font-size:22px;font-weight:700;color:#111827}
.arr{color:#2f80ed;font-size:18px;font-weight:bold}
.after{color:#2f80ed;font-size:22px;font-weight:700}
.unit{font-size:11px;color:#6b7280;margin-left:2px}
.meta{display:flex;flex-direction:column;gap:6px;margin-top:8px}
.mr{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}
.ml{font-size:11px;color:#6b7280;line-height:1.35;flex:1}
.mv{font-size:11px;color:#111827;font-weight:700;text-align:right;line-height:1.35;word-break:break-word}
.mv .b{color:#2f80ed}
.final-box{margin-top:8px;padding:9px 10px;background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px}
.final-title{font-size:11px;font-weight:700;color:#111827;margin-bottom:6px}
.final-list{display:flex;flex-direction:column;gap:5px}
.fi{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}
.fa{font-size:10px;color:#374151;font-weight:700;flex:1;word-break:break-word}
.fd{font-size:10px;color:#6b7280;text-align:right;flex:1;word-break:break-word}
.fd .amt{color:#2f80ed;font-weight:700}
.action-btn,.back-btn{display:block;text-align:center;padding:11px 12px;border-radius:10px;font-size:12px;font-weight:700;cursor:pointer;border:none;text-decoration:none}
.action-btn{width:100%;margin-top:10px;background:#2f80ed;color:#fff}
.action-btn:hover{background:#1769d1}
.detail-top{margin-bottom:12px}
.detail-heading{font-size:14px;font-weight:700;color:#111827}
.detail-sub{font-size:11px;color:#6b7280;margin-top:2px;line-height:1.4}
.ss{margin-top:10px;padding:10px;border-radius:12px;background:#eff6ff;border:1px solid #dbeafe}
.ss-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.ss-cell{background:#fff;border-radius:10px;padding:8px;border:1px solid #e5eefb}
.ss-label{font-size:10px;color:#6b7280;margin-bottom:3px}
.ss-value{font-size:12px;color:#111827;font-weight:700;word-break:break-word}
.accs{margin-top:12px}
.accs-title{font-size:12px;font-weight:700;color:#111827;margin-bottom:8px}
.acard{margin-top:10px;padding:12px;border:1px solid #dbeafe;background:#fbfdff;border-radius:14px}
.acard:first-child{margin-top:0}
.achip{display:inline-block;padding:4px 8px;border-radius:999px;background:#eaf2ff;color:#2f80ed;font-size:10px;font-weight:700;margin-bottom:6px}
.aname{font-size:12px;font-weight:700;color:#111827;word-break:break-word}
.asub{font-size:10px;color:#6b7280;margin-top:3px;word-break:break-word}
.ameta{display:flex;flex-direction:column;gap:7px;margin-top:10px}
.amr{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}
.aml{font-size:11px;color:#6b7280;line-height:1.4;flex:1}
.amv{font-size:11px;color:#111827;font-weight:700;text-align:right;word-break:break-word}
.amv .b{color:#2f80ed}
.anote{margin-top:10px;padding:9px 10px;background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px}
.anote-title{font-size:10px;font-weight:700;color:#111827;margin-bottom:4px}
.anote-text{font-size:10px;color:#6b7280;line-height:1.45;word-break:break-word}
.section{margin-top:12px;padding:10px;border:1px solid #e5eefb;border-radius:12px;background:#fbfdff}
.section-title{font-size:11px;font-weight:700;color:#111827;margin-bottom:8px}
.note-list{margin:0;padding-left:18px}
.note-list li{font-size:11px;color:#4b5563;line-height:1.5;margin-bottom:4px}
.btn-row{display:flex;gap:8px;margin-top:12px}
.btn-row>*{flex:1 1 0}
.back-btn{background:#fff;color:#2f80ed;border:1px solid #bfdbfe}
.back-btn:hover{background:#f8fbff}
@media(max-width:420px){
  body{padding:12px}.card{padding:11px}
  .old-price,.after{font-size:18px}
  .ss-grid{grid-template-columns:1fr}
}
</style>
</head>
<body>
<div class="container">
  <div class="card" id="sv"></div>
  <div class="card hidden" id="dv"></div>
</div>
<script>
const D = __OFFER_DATA__;
const ICON = "ICON_PLACEHOLDER";
const h = s => String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

function mr(label, value) {
  if (!value) return '';
  return `<div class="mr"><div class="ml">${h(label)}</div><div class="mv">${value}</div></div>`;
}
function amr(label, value) {
  if (!value) return '';
  return `<div class="amr"><div class="aml">${h(label)}</div><div class="amv">${value}</div></div>`;
}

function summaryHTML() {
  const badge = D.ncb_badge ? `<div class="badge">${h(D.ncb_badge)}</div>` : '';
  const balloon = (D.balloon_rows||[]).length
    ? `<div class="final-box"><div class="final-title">ค่างวดส่วนสุดท้าย</div><div class="final-list">${
        D.balloon_rows.map(r => {
          const [acc,term,pmt] = r.split('|');
          return `<div class="fi"><div class="fa">บัญชี ${h(acc)}</div><div class="fd">งวด ${h(term)} • <span class="amt">${h(pmt)} บาท</span></div></div>`;
        }).join('')
      }</div></div>`
    : '';
  return `
    <div class="header">
      <div class="icon"><img src="${ICON}" alt="icon"></div>
      <div class="title-wrap">
        <span class="plan-id">${h(D.plan_id)}</span>
        <div class="title">${h(D.plan_desc)}</div>${badge}
      </div>
    </div>
    <div class="account-bar">
      <div class="account-label">บัญชีที่พิจารณาเข้าร่วมมาตรการ</div>
      <div class="account-value">${h(D.accounts)}</div>
    </div>
    <div class="highlight-box">
      <div class="before-after">ลดค่างวดรายเดือน${h(D.step_label||'')}</div>
      <div class="price">
        <div class="old-price">${h(D.prev_inst)}</div>
        <div class="arr">→</div>
        <div><span class="after">${h(D.new_inst)}</span><span class="unit">บาท</span></div>
      </div>
    </div>
    <div class="meta">
      <div class="mr"><div class="ml">ภาระหนี้คงเหลือรวม</div><div class="mv">${h(D.total_os)} บาท</div></div>
      ${mr('พิจารณาข้อเสนอจาก', h(D.source_desc))}
      ${mr('อัตราดอกเบี้ย', D.int_rate_new ? `<span class="b">${h(D.int_rate_new)}</span>` : '')}
      ${mr('ระยะเวลาผ่อนชำระจากอัตราผ่อนชำระเดิม', h(D.term_actual_old))}
      ${mr('ระยะเวลาผ่อนชำระจากอัตราผ่อนชำระใหม่', D.term_remain_new ? `<span class="b">${h(D.term_remain_new)}</span>` : '')}
      ${mr('ระยะเวลาผ่อนชำระ', D.term_change ? `<span class="b">${h(D.term_change)}</span>` : '')}
      ${mr('ค่างวดผ่อนชำระในปีที่ 2 และ 3', D.inst_y2y3 ? `<span class="b">${h(D.inst_y2y3)}</span>` : '')}
      ${mr('อัตราผ่อนชำระภายหลังจาก 3 เดือน', D.inst_after_3m ? `<span class="b">${h(D.inst_after_3m)}</span>` : '')}
      ${mr('ดอกเบี้ยรวมตลอดสัญญา', h(D.int_total_change))}
    </div>
    ${balloon}
    <button type="button" class="action-btn" id="openBtn">ดูรายละเอียดและสมัคร</button>`;
}

function accHTML(a, idx) {
  const note = a.inelig_note
    ? `<div class="anote"><div class="anote-title">หมายเหตุ</div><div class="anote-text">${h(a.inelig_note)}</div></div>`
    : '';
  return `
    <div class="acard">
      <div class="achip">บัญชีที่ ${idx}</div>
      <div class="aname">${h(a.acc_name)}</div>
      <div class="asub">เลขที่บัญชี ${h(a.acc_no)}</div>
      <div class="ameta">
        <div class="amr"><div class="aml">ยอดหนี้คงเหลือ</div><div class="amv">${h(a.os)} บาท</div></div>
        <div class="amr"><div class="aml">อัตราดอกเบี้ย</div><div class="amv">${h(a.int_rate)}% ต่อปี</div></div>
        ${amr('ระยะเวลาผ่อนชำระตามสัญญาเดิม', h(a.term_old))}
        ${amr('ระยะเวลาผ่อนชำระ', a.term_change ? `<span class="b">${h(a.term_change)}</span>` : '')}
        ${amr('ค่างวดผ่อนชำระตามสัญญาเดิม', h(a.inst_old))}
        ${amr('ค่างวดผ่อนชำระ', a.inst_change ? `<span class="b">${h(a.inst_change)}</span>` : '')}
        ${amr('ค่างวดผ่อนชำระในปีแรก', a.inst_change_y1 ? `<span class="b">${h(a.inst_change_y1)}</span>` : '')}
        ${amr('ค่างวดผ่อนชำระในปีที่ 2 และ 3', a.inst_y2y3 ? `<span class="b">${h(a.inst_y2y3)}</span>` : '')}
        ${amr('อัตราผ่อนชำระภายหลังจาก 3 เดือน', a.inst_after_3m ? `<span class="b">${h(a.inst_after_3m)}</span>` : '')}
        ${amr('อัตราการผ่อนชำระของสินเชื่อเปิดใหม่', a.inst_new_loan ? `<span class="b">${h(a.inst_new_loan)}</span>` : '')}
        ${amr('ค่างวดชำระส่วนสุดท้ายหลังสิ้นสุดสัญญา', a.balloon_payment ? `<span class="b">${h(a.balloon_payment)}</span>` : '')}
        ${amr('ดอกเบี้ยรวมตลอดสัญญาตามสัญญาเดิม', h(a.int_total_old))}
        ${amr('ดอกเบี้ยรวมตลอดสัญญา', a.int_total_change ? `<span class="b">${h(a.int_total_change)}</span>` : '')}
      </div>
      ${note}
    </div>`;
}

function detailHTML() {
  const badge = D.ncb_badge ? `<div class="badge">${h(D.ncb_badge)}</div>` : '';
  const notes = (D.notes||[]).map(n=>`<li>${h(n)}</li>`).join('');
  return `
    <div class="detail-top">
      <div class="detail-heading">รายละเอียดมาตรการแยกตามบัญชี</div>
      <div class="detail-sub">กรุณาตรวจสอบเงื่อนไขและผลกระทบของแต่ละบัญชีก่อนสมัคร</div>
    </div>
    <div class="header">
      <div class="icon"><img src="${ICON}" alt="icon"></div>
      <div class="title-wrap">
        <span class="plan-id">${h(D.plan_id)}</span>
        <div class="title">${h(D.plan_desc)}</div>${badge}
      </div>
    </div>
    <div class="ss"><div class="ss-grid">
      <div class="ss-cell"><div class="ss-label">จำนวนบัญชีที่เข้าร่วม/พิจารณา</div><div class="ss-value">${h(D.cnt_eligible)}/${h(D.cnt_total)} บัญชี</div></div>
      <div class="ss-cell"><div class="ss-label">ภาระหนี้คงเหลือรวม</div><div class="ss-value">${h(D.total_os)} บาท</div></div>
      <div class="ss-cell"><div class="ss-label">ค่างวดรวมเดิม</div><div class="ss-value">${h(D.prev_inst)} บาท</div></div>
      <div class="ss-cell"><div class="ss-label">ค่างวดรวมใหม่</div><div class="ss-value">${h(D.new_inst)} บาท</div></div>
    </div></div>
    <div class="accs">
      <div class="accs-title">รายละเอียดรายบัญชี</div>
      ${(D.account_details||[]).map((a,i)=>accHTML(a,i+1)).join('')}
    </div>
    <div class="section">
      <div class="section-title">เงื่อนไขสำคัญ</div>
      <ul class="note-list">
        <li>ข้อเสนอนี้เป็นเพียงการประเมินเบื้องต้นจากข้อมูลที่มีอยู่ ณ ปัจจุบัน มิได้เป็นการรับประกันหรือยืนยันการอนุมัติ โดยผลการพิจารณาสุดท้ายจะเป็นไปตามหลักเกณฑ์และเงื่อนไขของธนาคาร</li>
        ${notes}
      </ul>
    </div>
    <div class="btn-row"><button type="button" class="back-btn" id="backBtn">ย้อนกลับ</button></div>`;
}

const sv = document.getElementById('sv');
const dv = document.getElementById('dv');
sv.innerHTML = summaryHTML();
dv.innerHTML = detailHTML();
document.getElementById('openBtn').addEventListener('click',()=>{sv.classList.add('hidden');dv.classList.remove('hidden');window.scrollTo({top:0,behavior:'smooth'});});
document.getElementById('backBtn').addEventListener('click',()=>{dv.classList.add('hidden');sv.classList.remove('hidden');window.scrollTo({top:0,behavior:'smooth'});});
</script>
</body>
</html>
""".replace("ICON_PLACEHOLDER", _ICON)
