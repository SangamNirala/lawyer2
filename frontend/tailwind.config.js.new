/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ["class"],
    content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
	extend: {
		borderRadius: {
			lg: 'var(--radius)',
			md: 'calc(var(--radius) - 2px)',
			sm: 'calc(var(--radius) - 4px)'
		},
		colors: {
			background: 'hsl(var(--background))',
			foreground: 'hsl(var(--foreground))',
			card: {
				DEFAULT: 'hsl(var(--card))',
				foreground: 'hsl(var(--card-foreground))'
			},
			popover: {
				DEFAULT: 'hsl(var(--popover))',
				foreground: 'hsl(var(--popover-foreground))'
			},
			primary: {
				DEFAULT: 'hsl(var(--primary))',
				foreground: 'hsl(var(--primary-foreground))'
			},
			secondary: {
				DEFAULT: 'hsl(var(--secondary))',
				foreground: 'hsl(var(--secondary-foreground))'
			},
			muted: {
				DEFAULT: 'hsl(var(--muted))',
				foreground: 'hsl(var(--muted-foreground))'
			},
			accent: {
				DEFAULT: 'hsl(var(--accent))',
				foreground: 'hsl(var(--accent-foreground))'
			},
			destructive: {
				DEFAULT: 'hsl(var(--destructive))',
				foreground: 'hsl(var(--destructive-foreground))'
			},
			border: 'hsl(var(--border))',
			input: 'hsl(var(--input))',
			ring: 'hsl(var(--ring))',
			chart: {
				'1': 'hsl(var(--chart-1))',
				'2': 'hsl(var(--chart-2))',
				'3': 'hsl(var(--chart-3))',
				'4': 'hsl(var(--chart-4))',
				'5': 'hsl(var(--chart-5))'
			}
		},
		keyframes: {
			'accordion-down': {
				from: {
					height: '0'
				},
				to: {
					height: 'var(--radix-accordion-content-height)'
				}
			},
			'accordion-up': {
				from: {
					height: 'var(--radix-accordion-content-height)'
				},
				to: {
					height: '0'
				}
			},
			'slide-in-right': {
				from: {
					transform: 'translateX(100%)'
				},
				to: {
					transform: 'translateX(0)'
				}
			},
			'slide-out-right': {
				from: {
					transform: 'translateX(0)'
				},
				to: {
					transform: 'translateX(100%)'
				}
			}
		},
		animation: {
			'accordion-down': 'accordion-down 0.2s ease-out',
			'accordion-up': 'accordion-up 0.2s ease-out',
			'slide-in-right': 'slide-in-right 0.3s ease-out',
			'slide-out-right': 'slide-out-right 0.3s ease-in'
		},
		spacing: {
			'18': '4.5rem',
			'88': '22rem',
			'safe-area-inset-bottom': 'env(safe-area-inset-bottom)'
		},
		screens: {
			'xs': '475px',
			'safe-area': { 'raw': '(display-mode: standalone)' }
		},
		minHeight: {
			'touch': '44px'
		},
		minWidth: {
			'touch': '44px'
		}
	}
  },
  plugins: [
    require("tailwindcss-animate"),
    function({ addUtilities }) {
      addUtilities({
        '.safe-area-inset-bottom': {
          'padding-bottom': 'env(safe-area-inset-bottom)'
        },
        '.safe-area-inset-top': {
          'padding-top': 'env(safe-area-inset-top)'
        }
      })
    }
  ],
};