/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["../views/*.*"],
  theme: {
    extend: {},
  },
  plugins: [],
  variants: {
    extend: {
      backgroundColor: ['odd', 'even'],
    },
  },
};
