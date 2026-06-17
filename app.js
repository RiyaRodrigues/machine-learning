// ==========================
// Bite Craft App JS
// ==========================

let selectedMeal = "Hi-Tea";
let selectedMood = "happy";
let selectedPref = "spicy";
let selectedHunger = "medium";

// --------------------------
// Section Navigation
// --------------------------
function showSection(id) {
    document.querySelectorAll(".section").forEach(sec => {
        sec.classList.remove("active");
    });

    const section = document.getElementById(id);
    if (section) section.classList.add("active");

    if (id === "browse") {
        loadBrowse("All");
    }
}

// --------------------------
// Chip Selection
// --------------------------
function selectChip(btn, type) {
    btn.parentElement.querySelectorAll(".chip").forEach(chip => {
        chip.classList.remove("active");
    });

    btn.classList.add("active");

    const value = btn.dataset.val;

    if (type === "meal") selectedMeal = value;
    if (type === "mood") selectedMood = value;
    if (type === "pref") selectedPref = value;
    if (type === "hunger") selectedHunger = value;
}

// --------------------------
// Recommendations
// --------------------------
async function getRecommendations() {

    try {

        const response = await fetch("/recommend", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                meal_time: selectedMeal,
                mood: selectedMood,
                preference: selectedPref,
                hunger: selectedHunger
            })
        });

        const data = await response.json();

        document.getElementById("rec-result").classList.remove("hidden");

        document.getElementById("seg-label").textContent =
            data.segment || "";

        document.getElementById("meal-label").textContent =
            data.meal_time || "";

        document.getElementById("cat-label").textContent =
            data.category || "";

        document.getElementById("mood-msg").textContent =
            data.mood_message || "";

        document.getElementById("meal-msg").textContent =
            data.meal_message || "";

        const grid = document.getElementById("rec-grid");
        grid.innerHTML = "";

        data.recommendations.forEach(item => {

            grid.innerHTML += `
                <div class="item-card">
                    <div class="item-icon">${item.icon}</div>
                    <div class="item-name">${item.name}</div>
                    <div class="item-price">Rs. ${item.price}</div>
                    <div class="item-humor">${item.humor}</div>

                    <div class="item-footer">
                        <button class="btn-add"
                            onclick="addToCart(${item.id})">
                            Add
                        </button>

                        <button class="btn-spin"
                            onclick="spinWheel(${item.id})">
                            🎡
                        </button>
                    </div>
                </div>
            `;
        });

    } catch (err) {
        console.error(err);
        showToast("Failed to get recommendations");
    }
}

// --------------------------
// Browse Menu
// --------------------------
async function loadBrowse(meal = "All") {

    const response = await fetch(`/browse?meal=${meal}`);
    const data = await response.json();

    const grid = document.getElementById("browse-grid");
    grid.innerHTML = "";

    data.items.forEach(item => {

        grid.innerHTML += `
            <div class="item-card">
                <div class="item-icon">${item.icon}</div>
                <div class="item-name">${item.name}</div>
                <div class="item-price">Rs. ${item.price}</div>
                <div class="item-humor">${item.humor}</div>

                <div class="item-footer">
                    <button class="btn-add"
                        onclick="addToCart(${item.id})">
                        Add
                    </button>
                </div>
            </div>
        `;
    });
}

function filterMeal(meal, btn) {

    document.querySelectorAll(".filter-tab")
        .forEach(tab => tab.classList.remove("active"));

    btn.classList.add("active");

    loadBrowse(meal);
}

function quickBrowse(meal) {
    showSection("browse");
    loadBrowse(meal);
}

// --------------------------
// Cart
// --------------------------
async function addToCart(id) {

    const response = await fetch("/add-to-cart", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            item_id: id
        })
    });

    const data = await response.json();

    updateCart(data);

    showToast("Added to cart 🛒");
}

async function removeFromCart(id) {

    const response = await fetch("/remove-from-cart", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            item_id: id
        })
    });

    const data = await response.json();

    updateCart(data);
}

async function clearCart() {

    await fetch("/clear-cart", {
        method: "POST"
    });

    loadCart();

    showToast("Cart cleared");
}

async function loadCart() {

    const response = await fetch("/get-cart");
    const data = await response.json();

    updateCart(data);
}

function updateCart(data) {

    document.getElementById("cart-count").textContent =
        data.count || 0;

    document.getElementById("cart-total").textContent =
        data.total || 0;

    const list = document.getElementById("cart-items");

    list.innerHTML = "";

    (data.cart || []).forEach(item => {

        list.innerHTML += `
            <div class="cart-item">
                <div class="cart-item-icon">${item.icon}</div>

                <div class="cart-item-name">
                    ${item.name}
                </div>

                <div class="cart-item-price">
                    Rs. ${item.price}
                </div>

                <button
                    class="cart-item-remove"
                    onclick="removeFromCart(${item.id})">
                    ✕
                </button>
            </div>
        `;
    });
}

// --------------------------
// Cart Drawer
// --------------------------
function toggleCart() {

    document
        .getElementById("cart-overlay")
        .classList.toggle("open");

    document
        .getElementById("cart-drawer")
        .classList.toggle("open");

    loadCart();
}

// --------------------------
// Spin Wheel
// --------------------------
async function spinWheel(id) {

    const response = await fetch("/spin-wheel", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            base_item_id: id
        })
    });

    const data = await response.json();

    if (data.success) {

        alert(
            `🎉 Suggested Combo: ${data.extra_item.name}`
        );
    }
}

// --------------------------
// Modal
// --------------------------
function closeModal() {

    document
        .getElementById("modal-overlay")
        .classList.remove("open");

    document
        .getElementById("item-modal")
        .classList.remove("open");
}

// --------------------------
// Order
// --------------------------
function placeOrder() {

    alert("🎉 Order placed successfully!");

    clearCart();
}

// --------------------------
// Toast
// --------------------------
function showToast(msg) {

    const toast = document.getElementById("toast");

    toast.textContent = msg;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 2500);
}

// --------------------------
// Initial Load
// --------------------------
window.onload = () => {
    loadBrowse("All");
    loadCart();
};