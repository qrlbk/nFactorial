This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000/en](http://localhost:3000/en) (or `/ru`, `/kk`) with your browser.

## Internationalization (i18n)

UI strings live in `messages/en.json`, `messages/ru.json`, and `messages/kk.json`. The app uses [next-intl](https://next-intl.dev) with locale prefixes (`/en`, `/ru`, `/kk`).

**Adding new UI text:**

1. Add the key to `messages/en.json` (source of truth).
2. Add matching translations to `messages/ru.json` and `messages/kk.json`.
3. Use `useTranslations('namespace')` and `t('key')` in components — avoid hardcoded user-visible strings.
4. Run `npm run check:i18n` to verify key parity and that ru/kk values are translated.

Runtime values from the API (pipeline status, trace status, threshold keys) go through helpers in `src/lib/i18n-display.ts`.

**Note:** Evaluator rejection reasons in `rejection_history` remain in English (backend limitation). The UI shows an “original” badge instead of auto-translating.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
