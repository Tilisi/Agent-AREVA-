const productsData = [
    { id: "prod_01", nom_fr: "Collagène Marin", nom_ar: "كولاجين بحري طبيعي", prix: 85.0, desc_fr: "Régénère la peau, les cheveux et les articulations.", desc_ar: "لتقوية البشرة والشعر والمفاصل وإعادة النضارة." },
    { id: "prod_02", nom_fr: "Brûle Graisse Naturel", nom_ar: "حارق دهون طبيعي", prix: 65.0, desc_fr: "Stimule le métabolisme et la combustion des graisses.", desc_ar: "مكمل طبيعي لحرق الدهون وتسريع الأيض بأمان." },
    { id: "prod_03", nom_fr: "Huile d'Argan Pure", nom_ar: "زيت أرغان خالص", prix: 45.0, desc_fr: "Huile 100% bio pressée à froid, hydratation intense.", desc_ar: "زيت أرغان 100% طبيعي لترطيب وتغذية البشرة." },
    { id: "prod_04", nom_fr: "Complément Multivitaminé", nom_ar: "مكمل فيتامينات متكامل", prix: 55.0, desc_fr: "Renforce l'immunité et réduit la fatigue quotidienne.", desc_ar: "لتعزيز المناعة اليومية ومحاربة الإرهاق والتعب." },
    { id: "prod_05", nom_fr: "Tisane Détox", nom_ar: "شاي أعشاب ديتوكس", prix: 35.0, desc_fr: "Plantes naturelles pour purifier l'organisme.", desc_ar: "لتنظيف الجسم وتحسين عملية الهضم بشكل طبيعي." },
    { id: "prod_06", nom_fr: "Crème Anti-Âge Naturelle", nom_ar: "كريم مقاوم للتجاعيد", prix: 95.0, desc_fr: "Soin raffermissant pour lisser les rides profondes.", desc_ar: "كريم طبيعي مشدود للبشرة غني بالعناصر المغذية." }
];

let currentLang = "fr";
const GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycb.../exec";
const WHATSAPP_PHONE = "+21620000000";

function switchLanguage(lang) {
    currentLang = lang;
    document.getElementById("btnFr").classList.toggle("active", lang === "fr");
    document.getElementById("btnAr").classList.toggle("active", lang === "ar");
    document.documentElement.setAttribute("dir", lang === "ar" ? "rtl" : "ltr");

    if (lang === "ar") {
        document.getElementById("heroTitle").innerText = "منتوجات التجميل والعناية الطبيعية";
        document.getElementById("heroSub").innerText = "تركيبات غنية بزيت الأرغان والألوفيرا. توصيل لكامل تراب الجمهورية خلال 24/48 ساعة.";
        document.getElementById("catalogTitle").innerText = "أبرز منتوجاتنا الطبيعية";
        document.getElementById("formTitle").innerText = "طلب سريع والدفع عند الاستلام";
        document.getElementById("lblProduct").innerText = "المنتوج المختار :";
        document.getElementById("lblQty").innerText = "الكمية المطلوبة :";
        document.getElementById("lblName").innerText = "الاسم واللقب :";
        document.getElementById("lblPhone").innerText = "رقم الهاتف :";
        document.getElementById("lblCity").innerText = "الولاية / المدينة :";
        document.getElementById("lblTotal").innerText = "المبلغ الإجمالي : ";
        document.getElementById("btnSubmit").innerText = "🛒 تأكيد وإرسال الطلب";
        document.getElementById("btnWa").innerText = "💬 للطلب المباشر عبر الواتساب";
    } else {
        document.getElementById("heroTitle").innerText = "Produits de Beauté & Bien-être Naturels";
        document.getElementById("heroSub").innerText = "Formules certifiées riches en Huile d'Argan et Aloe Vera. Livraison sur toute la Tunisie (24h/48h).";
        document.getElementById("catalogTitle").innerText = "Nos Produits Phares";
        document.getElementById("formTitle").innerText = "Commander Rapide & Paiement à la Livraison";
        document.getElementById("lblProduct").innerText = "Produit sélectionné :";
        document.getElementById("lblQty").innerText = "Quantité :";
        document.getElementById("lblName").innerText = "Nom & Prénom :";
        document.getElementById("lblPhone").innerText = "Numéro de Téléphone :";
        document.getElementById("lblCity").innerText = "Ville / Gouvernorat :";
        document.getElementById("lblTotal").innerText = "Total à payer : ";
        document.getElementById("btnSubmit").innerText = "🛒 Valider la Commande";
        document.getElementById("btnWa").innerText = "💬 Commander par WhatsApp";
    }

    renderProducts();
    updateTotal();
}

function renderProducts() {
    const grid = document.getElementById("productsGrid");
    grid.innerHTML = "";

    productsData.forEach(prod => {
        const nom = currentLang === "ar" ? prod.nom_ar : prod.nom_fr;
        const desc = currentLang === "ar" ? prod.desc_ar : prod.desc_fr;
        const btnText = currentLang === "ar" ? "اختر هذا المنتوج" : "Choisir ce produit";

        const card = document.createElement("div");
        card.className = "product-card";
        card.innerHTML = `
            <div>
                <h3 class="product-title">${nom}</h3>
                <p class="product-desc">${desc}</p>
            </div>
            <div>
                <div class="product-price">${prod.prix.toFixed(2)} TND</div>
                <button type="button" class="btn-select" onclick="selectProduct('${prod.id}')">${btnText}</button>
            </div>
        `;
        grid.appendChild(card);
    });
}

function selectProduct(prodId) {
    const prod = productsData.find(p => p.id === prodId);
    if (!prod) return;

    document.getElementById("selectedProductId").value = prod.id;
    document.getElementById("selectedProductName").value = currentLang === "ar" ? prod.nom_ar : prod.nom_fr;
    document.getElementById("selectedProductPrice").value = prod.prix;
    document.getElementById("displayProduct").value = `${currentLang === "ar" ? prod.nom_ar : prod.nom_fr} (${prod.prix.toFixed(2)} TND)`;

    updateTotal();
    document.getElementById("orderFormSection").scrollIntoView({ behavior: "smooth" });
}

function updateTotal() {
    const priceStr = document.getElementById("selectedProductPrice").value;
    const price = parseFloat(priceStr) || 0.0;
    const qty = parseInt(document.getElementById("quantity").value, 10) || 1;

    if (price === 0) {
        document.getElementById("totalPrice").innerText = "0.00 TND";
        return;
    }

    let total = price * qty;
    const frais = total >= 150.0 ? 0.0 : 7.0;
    total += frais;

    document.getElementById("totalPrice").innerText = `${total.toFixed(2)} TND ${frais === 0 ? '(Livraison Gratuite)' : '(+7 TND livraison)'}`;
}

document.getElementById("quantity").addEventListener("change", updateTotal);

document.getElementById("orderForm").addEventListener("submit", async function(e) {
    e.preventDefault();
    const statusDiv = document.getElementById("statusMessage");
    statusDiv.className = "status-message";
    statusDiv.style.display = "none";

    const prodId = document.getElementById("selectedProductId").value;
    if (!prodId) {
        alert(currentLang === "ar" ? "الرجاء اختيار منتوج أولاً." : "Veuillez d'abord sélectionner un produit.");
        return;
    }

    const payload = {
        productId: prodId,
        productName: document.getElementById("selectedProductName").value,
        quantity: document.getElementById("quantity").value,
        fullName: document.getElementById("fullName").value,
        phone: document.getElementById("phone").value,
        city: document.getElementById("city").value,
        totalPrice: document.getElementById("totalPrice").innerText,
        date: new Date().toISOString()
    };

    statusDiv.innerText = currentLang === "ar" ? "جاري إرسال الطلب..." : "Envoi de la commande en cours...";
    statusDiv.style.display = "block";

    try {
        const response = await fetch(GOOGLE_SCRIPT_URL, {
            method: "POST",
            mode: "no-cors",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        statusDiv.className = "status-message success";
        statusDiv.innerText = currentLang === "ar" ? "✅ تم تسجيل طلبك بنجاح! سيتصل بك فريق التوصيل قريباً." : "✅ Commande enregistrée avec succès ! Notre équipe vous contactera sous 24h.";
        document.getElementById("orderForm").reset();
        document.getElementById("selectedProductPrice").value = "0";
        updateTotal();
    } catch (err) {
        statusDiv.className = "status-message error";
        statusDiv.innerText = currentLang === "ar" ? "❌ حدث خطأ أثناء الإرسال. الرجاء المحاولة عبر الواتساب." : "❌ Erreur lors de l'envoi. Veuillez commander par WhatsApp.";
    }
});

function orderViaWhatsApp() {
    const prodName = document.getElementById("selectedProductName").value || (currentLang === "ar" ? "منتوج من الكاتالوغ" : "Produit du catalogue");
    const qty = document.getElementById("quantity").value || "1";
    const nom = document.getElementById("fullName").value || "";
    const phone = document.getElementById("phone").value || "";
    const city = document.getElementById("city").value || "";

    let text = "";
    if (currentLang === "ar") {
        text = `مرحبا، نحب نعدي طلبية من منتوجات أرفيا:\n📦 المنتوج: ${prodName}\n🔢 الكمية: ${qty}\n👤 الاسم: ${nom}\n📞 الهاتف: ${phone}\n📍 الولاية: ${city}`;
    } else {
        text = `Bonjour, je souhaite commander chez Arvea Nature :\n📦 Produit : ${prodName}\n🔢 Quantité : ${qty}\n👤 Nom : ${nom}\n📞 Téléphone : ${phone}\n📍 Ville : ${city}`;
    }

    const url = `https://api.whatsapp.com/send?phone=${encodeURIComponent(WHATSAPP_PHONE)}&text=${encodeURIComponent(text)}`;
    window.open(url, "_blank");
}

document.addEventListener("DOMContentLoaded", () => {
    renderProducts();
});
