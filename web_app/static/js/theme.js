document.addEventListener('DOMContentLoaded', function () {
    // Ensure Tailwind uses class strategy
    if (window.tailwind && tailwind.config) {
        tailwind.config.darkMode = 'class';
    }

    const themeToggleDesktop = document.getElementById('theme-toggle');
    const themeToggleMobile = document.getElementById('theme-toggle-mobile');
    const root = document.documentElement;

    // Helpers to swap icon visibility
    function showDarkIcons() {
        document.querySelectorAll('#theme-toggle-light-icon, #theme-toggle-mobile-light-icon').forEach(el => el.classList.add('hidden'));
        document.querySelectorAll('#theme-toggle-dark-icon, #theme-toggle-mobile-dark-icon').forEach(el => el.classList.remove('hidden'));
    }
    function showLightIcons() {
        document.querySelectorAll('#theme-toggle-dark-icon, #theme-toggle-mobile-dark-icon').forEach(el => el.classList.add('hidden'));
        document.querySelectorAll('#theme-toggle-light-icon, #theme-toggle-mobile-light-icon').forEach(el => el.classList.remove('hidden'));
    }

    // Set initial theme
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme === 'dark' || (!storedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        root.classList.add('dark');
        showDarkIcons();
    } else {
        root.classList.remove('dark');
        showLightIcons();
    }

    function toggleTheme() {
        root.classList.toggle('dark');
        const isDark = root.classList.contains('dark');
        if (isDark) {
            localStorage.setItem('theme', 'dark');
            showDarkIcons();
        } else {
            localStorage.setItem('theme', 'light');
            showLightIcons();
        }
    }

    if (themeToggleDesktop) themeToggleDesktop.addEventListener('click', toggleTheme);
    if (themeToggleMobile) themeToggleMobile.addEventListener('click', toggleTheme);
});
