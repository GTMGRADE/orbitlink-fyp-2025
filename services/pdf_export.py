# services/pdf_export.py
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import base64
from datetime import datetime

class AnalysisPDFExporter:
    """Generate PDF reports for YouTube analysis data"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the PDF"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0f1c3d'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#f24822'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#14294a'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
    
    def generate_report(self, project_name, analysis_data):
        """
        Generate a comprehensive PDF report
        
        Args:
            project_name: Name of the project
            analysis_data: Dictionary containing all analysis results
                - sentiment_analysis: Sentiment analysis data
                - influencers: Influencer detection data
                - community_detection: Community detection data
                - predictive_analysis: Predictive analysis data
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Title Page
        story.append(Paragraph("OrbitLink Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"<b>Project:</b> {project_name}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Add each analysis section
        if analysis_data.get('sentiment_analysis'):
            story.extend(self._add_sentiment_section(analysis_data['sentiment_analysis']))
            story.append(PageBreak())
        
        if analysis_data.get('influencers'):
            story.extend(self._add_influencers_section(analysis_data['influencers']))
            story.append(PageBreak())
        
        if analysis_data.get('community_detection'):
            story.extend(self._add_communities_section(analysis_data['community_detection']))
            story.append(PageBreak())
        
        if analysis_data.get('predictive_analysis'):
            story.extend(self._add_predictive_section(analysis_data['predictive_analysis']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _add_sentiment_section(self, sentiment_data):
        """Add sentiment analysis section to the report"""
        elements = []
        elements.append(Paragraph("1. Sentiment Analysis", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Overall sentiment score
        overall_score = sentiment_data.get('overall_score', 0)
        sentiment_label = "Positive" if overall_score > 0.1 else "Negative" if overall_score < -0.1 else "Neutral"
        
        elements.append(Paragraph(f"<b>Overall Sentiment:</b> {sentiment_label} ({overall_score:.2f})", self.styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Sentiment distribution
        label_counts = sentiment_data.get('label_counts', {})
        if label_counts:
            elements.append(Paragraph("Sentiment Distribution:", self.styles['SubHeader']))
            data = [
                ['Category', 'Count'],
                ['Positive', str(label_counts.get('positive', 0))],
                ['Neutral', str(label_counts.get('neutral', 0))],
                ['Negative', str(label_counts.get('negative', 0))]
            ]
            table = Table(data, colWidths=[2*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f24822')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 0.1*inch))
        
        # Add charts if available
        if sentiment_data.get('pie_chart'):
            elements.append(Paragraph("Sentiment Distribution Chart:", self.styles['SubHeader']))
            try:
                img_data = base64.b64decode(sentiment_data['pie_chart'])
                img_buffer = BytesIO(img_data)
                img = Image(img_buffer, width=4*inch, height=3*inch)
                elements.append(img)
            except Exception as e:
                elements.append(Paragraph(f"<i>Chart unavailable: {str(e)}</i>", self.styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        if sentiment_data.get('word_cloud'):
            elements.append(Paragraph("Word Cloud:", self.styles['SubHeader']))
            try:
                img_data = base64.b64decode(sentiment_data['word_cloud'])
                img_buffer = BytesIO(img_data)
                img = Image(img_buffer, width=5*inch, height=3*inch)
                elements.append(img)
            except Exception as e:
                elements.append(Paragraph(f"<i>Word cloud unavailable: {str(e)}</i>", self.styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Top comments
        top_comments = sentiment_data.get('top_like_comments', [])[:5]
        if top_comments:
            elements.append(Paragraph("Top 5 Most Liked Comments:", self.styles['SubHeader']))
            for i, comment in enumerate(top_comments, 1):
                text = comment.get('text', '')[:200] + ('...' if len(comment.get('text', '')) > 200 else '')
                likes = comment.get('like_count', 0)
                sentiment = comment.get('label', 'neutral')
                elements.append(Paragraph(
                    f"<b>{i}.</b> {text}<br/><i>Likes: {likes} | Sentiment: {sentiment}</i>",
                    self.styles['Normal']
                ))
                elements.append(Spacer(1, 0.08*inch))
        
        return elements
    
    def _add_influencers_section(self, influencers_data):
        """Add influencer detection section to the report"""
        elements = []
        elements.append(Paragraph("2. Identify Influencers", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.1*inch))
        
        influencers = influencers_data[:15]  # Top 15 influencers
        
        if influencers:
            elements.append(Paragraph(f"Top {len(influencers)} Influencers:", self.styles['SubHeader']))
            
            # Create table
            data = [['Rank', 'Name', 'Score', 'Comments', 'Influence']]
            for i, influencer in enumerate(influencers, 1):
                data.append([
                    str(i),
                    influencer.get('author_name', 'Unknown')[:30],
                    f"{influencer.get('influencer_score', 0):.2f}",
                    str(influencer.get('comment_count', 0)),
                    influencer.get('influence_type', 'N/A')
                ])
            
            table = Table(data, colWidths=[0.5*inch, 2*inch, 0.8*inch, 0.8*inch, 1.2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f24822')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("<i>No influencer data available</i>", self.styles['Normal']))
        
        return elements
    
    def _add_communities_section(self, community_data):
        """Add community detection section to the report"""
        elements = []
        elements.append(Paragraph("3. Detect Communities", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.1*inch))
        
        num_communities = community_data.get('num_communities', 0)
        modularity = community_data.get('modularity', 0)
        
        elements.append(Paragraph(f"<b>Total Communities Detected:</b> {num_communities}", self.styles['Normal']))
        elements.append(Paragraph(f"<b>Modularity Score:</b> {modularity:.3f}", self.styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Communities table
        communities = community_data.get('communities', [])[:10]  # Top 10 communities
        if communities:
            elements.append(Paragraph("Top Communities:", self.styles['SubHeader']))
            
            data = [['ID', 'Size', 'Comments', 'Avg Sentiment']]
            for comm in communities:
                data.append([
                    str(comm.get('community_id', 'N/A')),
                    str(comm.get('size', 0)),
                    str(comm.get('total_comments', 0)),
                    f"{comm.get('avg_sentiment', 0):.2f}"
                ])
            
            table = Table(data, colWidths=[0.8*inch, 1*inch, 1.2*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f24822')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
        
        # Add visualization if available
        if community_data.get('network_visualization'):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("Community Network:", self.styles['SubHeader']))
            try:
                img_data = base64.b64decode(community_data['network_visualization'])
                img_buffer = BytesIO(img_data)
                img = Image(img_buffer, width=5*inch, height=4*inch)
                elements.append(img)
            except Exception as e:
                elements.append(Paragraph(f"<i>Visualization unavailable: {str(e)}</i>", self.styles['Normal']))
        
        return elements
    
    def _add_predictive_section(self, predictive_data):
        """Add predictive analysis section to the report"""
        elements = []
        elements.append(Paragraph("4. Predictive Analysis", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.1*inch))
        
        if not predictive_data.get('has_data'):
            elements.append(Paragraph("<i>Insufficient historical data for predictions</i>", self.styles['Normal']))
            return elements
        
        elements.append(Paragraph(
            f"<b>Based on {predictive_data.get('historical_count', 0)} historical analyses</b>",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.1*inch))
        
        # Engagement forecast
        engagement = predictive_data.get('engagement_forecast', {})
        elements.append(Paragraph("Engagement Forecast:", self.styles['SubHeader']))
        elements.append(Paragraph(
            f"<b>Trend:</b> {engagement.get('trend', 'Unknown').title()}<br/>"
            f"<b>Change:</b> {engagement.get('percentage', 0):+.1f}%<br/>"
            f"<b>Confidence:</b> {engagement.get('confidence', 0)}%<br/>"
            f"<b>Description:</b> {engagement.get('description', 'N/A')}",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.1*inch))
        
        # Sentiment trends
        sentiment = predictive_data.get('sentiment_trends', {})
        elements.append(Paragraph("Sentiment Trends:", self.styles['SubHeader']))
        elements.append(Paragraph(
            f"<b>Current Score:</b> {sentiment.get('current_score', 0):.2f}<br/>"
            f"<b>Trend:</b> {sentiment.get('trend', 'Unknown').title()}<br/>"
            f"<b>Forecast:</b> {sentiment.get('forecast', 0):.2f}<br/>"
            f"<b>Confidence:</b> {sentiment.get('confidence', 0)}%",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.1*inch))
        
        # Growth prediction
        growth = predictive_data.get('growth_prediction', {})
        elements.append(Paragraph("Growth Prediction:", self.styles['SubHeader']))
        elements.append(Paragraph(
            f"<b>Rate:</b> {growth.get('rate', 0):+.1f}%<br/>"
            f"<b>Timeframe:</b> {growth.get('timeframe', 'N/A')}<br/>"
            f"<b>Confidence:</b> {growth.get('confidence', 0)}%<br/>"
            f"<b>Description:</b> {growth.get('description', 'N/A')}",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.1*inch))
        
        # Upcoming predictions
        upcoming = predictive_data.get('upcoming_predictions', [])
        if upcoming:
            elements.append(Paragraph("Upcoming Predictions:", self.styles['SubHeader']))
            for pred in upcoming:
                elements.append(Paragraph(
                    f"<b>{pred.get('timeframe')}:</b> {pred.get('prediction')} "
                    f"<i>({pred.get('confidence')}% confidence)</i>",
                    self.styles['Normal']
                ))
                elements.append(Spacer(1, 0.05*inch))
        
        return elements
