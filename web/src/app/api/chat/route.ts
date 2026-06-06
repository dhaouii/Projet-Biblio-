import { GoogleGenerativeAI } from '@google/generative-ai';
import { getBooks, getStats } from '@/app/actions';
import { NextResponse } from 'next/server';

// La clé est lue depuis la variable d'environnement (jamais codée en dur).
const API_KEY = process.env.GEMINI_API_KEY ?? "";
const genAI = new GoogleGenerativeAI(API_KEY);

const SYSTEM_PROMPT = `Tu es l'assistant intelligent de la Bibliothèque Universitaire.
Tu t'appelles "BiblioBot" et tu aides les étudiants et lecteurs.

Règles importantes :
- Réponds UNIQUEMENT en français
- Utilise les données réelles fournies dans le contexte
- Sois naturel, chaleureux et utile
- Si un livre est emprunté, dis-le clairement
- Pour les recommandations, base-toi sur les catégories et statuts disponibles
- N'invente JAMAIS de données qui ne sont pas dans le contexte fourni
- Sois concis mais complet dans tes réponses
- Utilise des emojis avec parcimonie pour rendre les réponses plus lisibles

Tu peux répondre à :
- La disponibilité d'un livre spécifique
- La recherche par auteur ou catégorie  
- Les recommandations selon le goût du lecteur
- L'existence d'un livre par ID ou titre
- Les statistiques générales de la bibliothèque`;

export async function POST(req: Request) {
  let userMessage = '';
  try {
    const body = await req.json();
    userMessage = body.message;

    if (!userMessage) {
      return NextResponse.json({ error: 'Message is required' }, { status: 400 });
    }

    // Fetch live data from SQLite
    const books = await getBooks();
    const stats = await getStats();

    // Format context (similar to python's book_service.get_context_for_chatbot)
    const booksListText = books
      .map(b => `[ID: ${b.id}] "${b.titre}" par ${b.auteur} | Catégorie: ${b.categorie} | Statut: ${b.statut} | Dispo: ${b.quantite}`)
      .join('\\n');

    const context = `Statistiques de la bibliothèque:
Total livres: ${stats.total}
Disponibles: ${stats.disponibles}
Empruntés: ${stats.empruntes}

Liste des livres:
${booksListText}`;

    const fullPrompt = `
${SYSTEM_PROMPT}

=== DONNÉES ACTUELLES DE LA BIBLIOTHÈQUE ===
${context}
===========================================

Question du lecteur : ${userMessage}

Réponds en te basant UNIQUEMENT sur les données ci-dessus.`;

    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash-latest" });
    const result = await model.generateContent(fullPrompt);
    const response = await result.response;
    const text = response.text();

    return NextResponse.json({ response: text });

  } catch (error: any) {
    console.error('Chat API Error:', error);
    
    // Fallback logic (Mode dégradé) exactly as specified in the python code
    const q = userMessage.toLowerCase();
    const books = await getBooks();
    const stats = await getStats();

    // Recherche par auteur locale
    const matchedAuthor = books.find(b => q.includes(b.auteur.toLowerCase()));
    if (matchedAuthor) {
      const sameAuthor = books.filter(b => b.auteur === matchedAuthor.auteur);
      let result = `📚 Livres de ${matchedAuthor.auteur} dans notre catalogue :\n`;
      for (const b of sameAuthor) {
        const emoji = b.statut === 'disponible' ? '✅' : '📤';
        result += `  ${emoji} '${b.titre}' (${b.annee_publication}) — ${b.statut}\n`;
      }
      return NextResponse.json({ response: result });
    }

    // Recherche de disponibilité locale
    if (q.includes('disponible') || q.includes('disponibles') || q.includes('peut-on emprunter')) {
      const available = books.filter(b => b.statut === 'disponible');
      let result = `✅ ${available.length} livre(s) disponible(s) :\n`;
      for (const b of available.slice(0, 8)) {
        result += `  • '${b.titre}' — ${b.auteur}\n`;
      }
      return NextResponse.json({ response: result });
    }

    // Statistiques locales
    if (q.includes('combien') || q.includes('total') || q.includes('statistique') || q.includes('stats')) {
      const result = `📊 Statistiques de la bibliothèque :\n` +
                     `  • Total : ${stats.total} livres\n` +
                     `  • Disponibles : ${stats.disponibles}\n` +
                     `  • Empruntés : ${stats.empruntes}\n` +
                     `  • Réservés : ${stats.reserves}\n` +
                     `  • Catégories : ${stats.categories}`;
      return NextResponse.json({ response: result });
    }

    // Default fallback
    const result = `💡 Mode hors-ligne activé (L'API IA est indisponible).\nLa bibliothèque contient actuellement ${stats.total} livres dont ${stats.disponibles} disponibles.`;
    return NextResponse.json({ response: result });
  }
}
