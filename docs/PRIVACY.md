# Privacy Policy

**Privacy-Focused AI Document Summarizer**  
*Effective Date: January 1, 2024*  
*Last Updated: January 1, 2024*

## 🔒 Our Privacy Commitment

The Privacy-Focused AI Document Summarizer is built with **privacy by design**. We are committed to protecting your data and ensuring that your documents and personal information remain completely under your control.

## 🏠 100% Local Processing

### What This Means
- **All document processing happens on your device** - your documents never leave your computer
- **No cloud services** - we don't use any external APIs for document analysis
- **No data transmission** - your content is never sent to our servers or any third-party services
- **Offline operation** - the application works completely offline (except for optional model updates)

### Your Documents Stay Private
- PDF and DOCX files are processed locally using your computer's resources
- Text extraction and AI summarization occur entirely on your device
- Generated summaries are stored only in your local encrypted database
- No copies of your documents or summaries are transmitted anywhere

## 🗄️ Local Data Storage

### What We Store Locally
We store the following data in an encrypted SQLite database on your device:

- **Document summaries** (not the original documents)
- **Document metadata** (filename, file size, processing date)
- **Application settings** and user preferences
- **Processing statistics** (for performance monitoring)

### What We Don't Store
- **Original document content** - documents are processed and discarded
- **Personal identifying information** - no names, emails, or personal data
- **User accounts** - no registration or login required
- **Usage analytics** - no tracking or analytics data collection

### Database Encryption
- Your local database is encrypted using industry-standard encryption
- You control the encryption key
- Without your key, the data is unreadable
- Optional: Use password-based encryption for additional security

## 🔄 Model Updates (Optional)

### How Model Updates Work
- We check for AI model updates from our servers or GitHub releases
- Only version information is transmitted (no personal data)
- Model downloads are optional and user-controlled
- You can disable automatic update checks in settings

### What's Transmitted During Updates
- Current model version number
- Your operating system type (Windows/macOS)
- No personal information or document data

### No Tracking
- We don't track who downloads updates
- No analytics or usage data is collected
- No user identification or device fingerprinting

## 🛡️ Data Security

### Encryption
- **Database encryption**: All local data is encrypted at rest
- **Secure key management**: Encryption keys are stored locally and under your control
- **No plain text storage**: Sensitive data is never stored in plain text

### Access Controls
- **Application-level security**: Only the application can access your data
- **File system permissions**: Database files have restricted access permissions
- **No remote access**: No backdoors or remote access capabilities

### Data Integrity
- **Regular backups**: You can create encrypted backups of your data
- **Corruption protection**: Database integrity checks prevent data corruption
- **Version control**: Settings and preferences are versioned for recovery

## 🚫 What We Don't Do

### No Data Collection
- We don't collect personal information
- We don't track your usage patterns
- We don't store analytics or telemetry data
- We don't profile users or create user accounts

### No Third-Party Sharing
- We don't share data with third parties
- We don't sell data to advertisers
- We don't use data for marketing purposes
- We don't integrate with external analytics services

### No Cloud Dependencies
- We don't use cloud storage services
- We don't require internet connectivity for core functionality
- We don't sync data across devices (unless you explicitly choose to)
- We don't backup data to external services

## 👤 Your Rights and Control

### Complete Control
- **Your data, your device**: All data remains on your computer
- **Delete anytime**: Remove all data by uninstalling the application
- **Export capability**: Export your summaries in standard formats
- **No vendor lock-in**: Your data is in standard formats (SQLite, JSON, CSV)

### Transparency
- **Open source option**: Core privacy components can be audited
- **Clear documentation**: All data handling is documented
- **No hidden features**: No undisclosed data collection or transmission

### Backup and Recovery
- **Local backups**: Create encrypted backups of your data
- **Data portability**: Export data in multiple formats
- **Migration tools**: Move data between installations
- **Recovery options**: Restore from backups if needed

## 🔍 Technical Implementation

### Privacy by Design Architecture

1. **Local-First Design**
   - All processing occurs on your device
   - No network dependencies for core features
   - Encrypted local storage

2. **Minimal Data Collection**
   - Only essential data for functionality
   - No unnecessary metadata collection
   - User-controlled data retention

3. **Secure Communication**
   - HTTPS for optional model updates
   - No personal data in network requests
   - Certificate validation for security

### Data Flow

```
Your Document → Local Processing → Encrypted Storage → Your Control
     ↓              ↓                    ↓              ↓
  [PDF/DOCX]    [Text Extract]      [Local SQLite]   [View/Export]
     ↓              ↓                    ↓              ↓
  Never Sent    AI Processing       Encrypted DB     Always Local
```

## 📋 Compliance and Standards

### Industry Standards
- **Encryption**: AES-256 encryption for data at rest
- **Security**: Following OWASP security guidelines
- **Privacy**: Aligned with GDPR and CCPA principles
- **Transparency**: Clear documentation of all data practices

### No Legal Obligations
Since we don't collect personal data:
- No data breach notification requirements
- No data subject requests to process
- No cross-border data transfer concerns
- No data retention policy complexities

## 🚀 Getting Started Securely

### Initial Setup
1. **Installation**: Download from official sources only
2. **Database encryption**: Set up encryption during first run
3. **Settings review**: Configure privacy preferences
4. **Model download**: Optionally download AI models locally

### Best Practices
- **Strong encryption key**: Use a strong, unique encryption key
- **Regular backups**: Create encrypted backups of important summaries
- **Keep updated**: Install security updates when available
- **Secure environment**: Use the application on a secure, updated system

## 🆘 Questions and Support

### Contact Information
- **Documentation**: Check our comprehensive docs in the `docs/` folder
- **Issues**: Report technical issues on our GitHub repository
- **Community**: Join community discussions for general questions

### No Personal Support Data
- We don't require personal information for support
- Support requests can be made anonymously
- No support ticket tracking or customer databases

## 📝 Changes to This Policy

### Updates
- Privacy policy changes will be documented in version control
- Major changes will be highlighted in release notes
- You maintain control over your data regardless of policy changes

### Notification
- Updates published with new software versions
- No email notifications (we don't have your email)
- Check this document for the latest version

---

## 🎯 Summary: Your Privacy Guarantee

✅ **Your documents never leave your device**  
✅ **All processing happens locally**  
✅ **Encrypted database under your control**  
✅ **No user accounts or personal data collection**  
✅ **No third-party data sharing**  
✅ **Optional model updates only**  
✅ **Complete data portability**  
✅ **Open and transparent practices**

**This is more than a privacy policy - it's our architecture. Privacy isn't just our promise, it's how we built the application.**

---

*For technical details about our privacy implementation, see the [Development Guide](DEVELOPMENT.md) and review our open-source code.* 