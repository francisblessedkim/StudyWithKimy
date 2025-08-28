/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",       // for global templates
    "./**/templates/**/*.html",    // for app-level templates
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

