from datetime import datetime, timedelta
from config import Config
import json

class DigestGenerator:
    def __init__(self, database, processor, audio_gen, email_handler):
        self.db = database
        self.processor = processor
        self.audio_gen = audio_gen
        self.email_handler = email_handler

    def send_daily_digest(self):
        """Generate and send the daily digest email"""
        # Get unread articles from the last 24 hours
        articles = self.db.get_unread_articles_for_digest(hours=24)

        if len(articles) == 0:
            print("No new articles for digest")
            return

        # Generate cross-article insights
        cross_article_insights = self.processor.generate_cross_article_insights(articles)

        # Save digest to database
        article_ids = [a['id'] for a in articles]
        digest_id = self.db.add_digest(article_ids, cross_article_insights)

        # Generate digest email HTML
        html_content = self._build_digest_html(articles, cross_article_insights)
        text_content = self._build_digest_text(articles, cross_article_insights)

        # Send email
        subject = f"Your Daily Reading Digest - {len(articles)} New Articles"
        success = self.email_handler.send_email(
            Config.DIGEST_EMAIL,
            subject,
            html_content,
            text_content
        )

        if success:
            print(f"Digest sent successfully: {len(articles)} articles")
        else:
            print("Failed to send digest")

        return digest_id

    def _build_digest_html(self, articles, cross_article_insights):
        """Build HTML email content for digest"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1a1a1a;
            font-size: 24px;
            margin-bottom: 10px;
        }}
        .date {{
            color: #666;
            font-size: 14px;
            margin-bottom: 20px;
        }}
        .insights {{
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 4px;
        }}
        .insights h2 {{
            margin-top: 0;
            font-size: 18px;
            color: #007bff;
        }}
        .article {{
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .article:last-child {{
            border-bottom: none;
        }}
        .article-title {{
            font-size: 18px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 8px;
        }}
        .article-meta {{
            color: #666;
            font-size: 13px;
            margin-bottom: 12px;
        }}
        .summary {{
            color: #333;
            margin-bottom: 12px;
        }}
        .insights-list {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .insights-list li {{
            margin-bottom: 8px;
            color: #444;
        }}
        .implications {{
            background-color: #fff9e6;
            padding: 12px;
            border-radius: 4px;
            margin-top: 10px;
            font-size: 14px;
        }}
        .actions {{
            margin-top: 15px;
        }}
        .btn {{
            display: inline-block;
            padding: 8px 16px;
            margin-right: 10px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 14px;
        }}
        .btn-secondary {{
            background-color: #6c757d;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Your Daily Reading Digest</h1>
        <div class="date">{datetime.now().strftime('%B %d, %Y')}</div>

        <p>You have <strong>{len(articles)} new article{"s" if len(articles) != 1 else ""}</strong> in your reading list.</p>
"""

        # Add cross-article insights if available
        if cross_article_insights:
            html += f"""
        <div class="insights">
            <h2>Key Themes & Insights</h2>
            <p>{cross_article_insights.replace(chr(10), '<br>')}</p>
        </div>
"""

        # Add each article
        for idx, article in enumerate(articles, 1):
            key_insights = article.get('key_insights', [])
            if isinstance(key_insights, str):
                try:
                    key_insights = json.loads(key_insights)
                except:
                    key_insights = []

            html += f"""
        <div class="article">
            <div class="article-title">{idx}. {article.get('title', 'Untitled')}</div>
            <div class="article-meta">
                {article.get('source', 'Unknown source')}
                {f"• {article.get('author')}" if article.get('author') else ''}
            </div>

            <div class="summary">{article.get('summary', 'No summary available')}</div>
"""

            if key_insights and len(key_insights) > 0:
                html += """
            <ul class="insights-list">
"""
                for insight in key_insights:
                    html += f"                <li>{insight}</li>\n"
                html += """
            </ul>
"""

            if article.get('implications'):
                html += f"""
            <div class="implications">
                <strong>Why it matters:</strong> {article.get('implications')}
            </div>
"""

            # Add action buttons
            article_url = article.get('url', '#')
            html += f"""
            <div class="actions">
                <a href="{article_url}" class="btn">Read Article</a>
                <a href="http://localhost:5000/api/articles/{article['id']}/read" class="btn btn-secondary">Mark as Read</a>
            </div>
        </div>
"""

        html += """
        <div class="footer">
            <p>Visit your <a href="http://localhost:5000">Reading Dashboard</a> to manage your articles</p>
        </div>
    </div>
</body>
</html>
"""

        return html

    def _build_digest_text(self, articles, cross_article_insights):
        """Build plain text email content for digest"""
        text = f"Your Daily Reading Digest - {datetime.now().strftime('%B %d, %Y')}\n"
        text += "=" * 60 + "\n\n"
        text += f"You have {len(articles)} new article{'s' if len(articles) != 1 else ''} in your reading list.\n\n"

        if cross_article_insights:
            text += "KEY THEMES & INSIGHTS:\n"
            text += "-" * 60 + "\n"
            text += cross_article_insights + "\n\n"

        for idx, article in enumerate(articles, 1):
            text += f"\n{idx}. {article.get('title', 'Untitled')}\n"
            text += f"   Source: {article.get('source', 'Unknown')}\n"
            if article.get('author'):
                text += f"   Author: {article.get('author')}\n"
            text += f"   URL: {article.get('url', '')}\n\n"

            if article.get('summary'):
                text += f"   {article.get('summary')}\n\n"

            key_insights = article.get('key_insights', [])
            if isinstance(key_insights, str):
                try:
                    key_insights = json.loads(key_insights)
                except:
                    key_insights = []

            if key_insights:
                text += "   Key Insights:\n"
                for insight in key_insights:
                    text += f"   • {insight}\n"
                text += "\n"

            if article.get('implications'):
                text += f"   Why it matters: {article.get('implications')}\n\n"

            text += "-" * 60 + "\n"

        return text
