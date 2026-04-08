import React, { useState } from 'react';
import { createResume, createInvoice, createBudget } from '../../services/api';

interface OfficeToolsProps {
  onDocumentCreated?: (filename: string) => void;
}

const OfficeTools: React.FC<OfficeToolsProps> = ({ onDocumentCreated }) => {
  const [loading, setLoading] = useState<string | null>(null);
  const [resumeData, setResumeData] = useState({
    name: '',
    email: '',
    phone: '',
    summary: '',
    experience: [{ title: '', company: '', description: '' }],
    education: [{ degree: '', school: '' }],
    skills: [] as string[],
    skillInput: '',
  });

  const [invoiceData, setInvoiceData] = useState({
    number: '',
    customer: '',
    items: [{ description: '', quantity: 1, unit_price: 0 }],
  });

  const [budgetData, setBudgetData] = useState({
    name: '',
    categories: [{ name: '', budgeted: 0, actual: 0 }],
  });

  const handleCreateResume = async () => {
    setLoading('resume');
    try {
      const blob = await createResume(resumeData);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `resume_${resumeData.name.replace(/\s/g, '_')}.docx`;
      a.click();
      URL.revokeObjectURL(url);
      onDocumentCreated?.(`resume_${resumeData.name}.docx`);
    } catch (error) {
      console.error('Failed to create resume:', error);
      alert('Failed to create resume. Please try again.');
    } finally {
      setLoading(null);
    }
  };

  const handleCreateInvoice = async () => {
    setLoading('invoice');
    try {
      const blob = await createInvoice(invoiceData);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `invoice_${invoiceData.number}.docx`;
      a.click();
      URL.revokeObjectURL(url);
      onDocumentCreated?.(`invoice_${invoiceData.number}.docx`);
    } catch (error) {
      console.error('Failed to create invoice:', error);
      alert('Failed to create invoice. Please try again.');
    } finally {
      setLoading(null);
    }
  };

  const handleCreateBudget = async () => {
    setLoading('budget');
    try {
      const blob = await createBudget(budgetData);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `budget_${budgetData.name.replace(/\s/g, '_')}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
      onDocumentCreated?.(`budget_${budgetData.name}.xlsx`);
    } catch (error) {
      console.error('Failed to create budget:', error);
      alert('Failed to create budget. Please try again.');
    } finally {
      setLoading(null);
    }
  };

  const addExperience = () => {
    setResumeData({
      ...resumeData,
      experience: [...resumeData.experience, { title: '', company: '', description: '' }],
    });
  };

  const addEducation = () => {
    setResumeData({
      ...resumeData,
      education: [...resumeData.education, { degree: '', school: '' }],
    });
  };

  const addSkill = () => {
    if (resumeData.skillInput.trim()) {
      setResumeData({
        ...resumeData,
        skills: [...resumeData.skills, resumeData.skillInput.trim()],
        skillInput: '',
      });
    }
  };

  const addInvoiceItem = () => {
    setInvoiceData({
      ...invoiceData,
      items: [...invoiceData.items, { description: '', quantity: 1, unit_price: 0 }],
    });
  };

  const addBudgetCategory = () => {
    setBudgetData({
      ...budgetData,
      categories: [...budgetData.categories, { name: '', budgeted: 0, actual: 0 }],
    });
  };

  return (
    <div className="office-tools">
      <h3>📝 DarkmoorAI Office Suite</h3>
      
      {/* Resume Builder */}
      <div className="office-section">
        <h4>📄 Create Resume</h4>
        <div className="office-form">
          <input
            type="text"
            placeholder="Full Name"
            value={resumeData.name}
            onChange={(e) => setResumeData({ ...resumeData, name: e.target.value })}
          />
          <input
            type="email"
            placeholder="Email"
            value={resumeData.email}
            onChange={(e) => setResumeData({ ...resumeData, email: e.target.value })}
          />
          <input
            type="tel"
            placeholder="Phone"
            value={resumeData.phone}
            onChange={(e) => setResumeData({ ...resumeData, phone: e.target.value })}
          />
          <textarea
            placeholder="Professional Summary"
            rows={3}
            value={resumeData.summary}
            onChange={(e) => setResumeData({ ...resumeData, summary: e.target.value })}
          />
          
          <h5>💼 Experience</h5>
          {resumeData.experience.map((exp, idx) => (
            <div key={idx} className="experience-entry">
              <input
                type="text"
                placeholder="Job Title"
                value={exp.title}
                onChange={(e) => {
                  const newExp = [...resumeData.experience];
                  newExp[idx].title = e.target.value;
                  setResumeData({ ...resumeData, experience: newExp });
                }}
              />
              <input
                type="text"
                placeholder="Company"
                value={exp.company}
                onChange={(e) => {
                  const newExp = [...resumeData.experience];
                  newExp[idx].company = e.target.value;
                  setResumeData({ ...resumeData, experience: newExp });
                }}
              />
              <textarea
                placeholder="Description"
                rows={2}
                value={exp.description}
                onChange={(e) => {
                  const newExp = [...resumeData.experience];
                  newExp[idx].description = e.target.value;
                  setResumeData({ ...resumeData, experience: newExp });
                }}
              />
            </div>
          ))}
          <button onClick={addExperience}>+ Add Experience</button>
          
          <h5>🎓 Education</h5>
          {resumeData.education.map((edu, idx) => (
            <div key={idx} className="education-entry">
              <input
                type="text"
                placeholder="Degree"
                value={edu.degree}
                onChange={(e) => {
                  const newEdu = [...resumeData.education];
                  newEdu[idx].degree = e.target.value;
                  setResumeData({ ...resumeData, education: newEdu });
                }}
              />
              <input
                type="text"
                placeholder="School"
                value={edu.school}
                onChange={(e) => {
                  const newEdu = [...resumeData.education];
                  newEdu[idx].school = e.target.value;
                  setResumeData({ ...resumeData, education: newEdu });
                }}
              />
            </div>
          ))}
          <button onClick={addEducation}>+ Add Education</button>
          
          <h5>🔧 Skills</h5>
          <div className="skills-list">
            {resumeData.skills.map((skill, idx) => (
              <span key={idx} className="skill-tag">
                {skill}
                <button onClick={() => {
                  const newSkills = resumeData.skills.filter((_, i) => i !== idx);
                  setResumeData({ ...resumeData, skills: newSkills });
                }}>×</button>
              </span>
            ))}
          </div>
          <div className="skills-input">
            <input
              type="text"
              placeholder="Add skill"
              value={resumeData.skillInput}
              onChange={(e) => setResumeData({ ...resumeData, skillInput: e.target.value })}
              onKeyPress={(e) => e.key === 'Enter' && addSkill()}
            />
            <button onClick={addSkill}>Add</button>
          </div>
          
          <button 
            className="create-btn" 
            onClick={handleCreateResume} 
            disabled={loading === 'resume'}
          >
            {loading === 'resume' ? 'Creating...' : '📄 Create Resume'}
          </button>
        </div>
      </div>
      
      {/* Invoice Builder */}
      <div className="office-section">
        <h4>🧾 Create Invoice</h4>
        <div className="office-form">
          <input
            type="text"
            placeholder="Invoice Number (e.g., INV-001)"
            value={invoiceData.number}
            onChange={(e) => setInvoiceData({ ...invoiceData, number: e.target.value })}
          />
          <textarea
            placeholder="Customer Information"
            rows={3}
            value={invoiceData.customer}
            onChange={(e) => setInvoiceData({ ...invoiceData, customer: e.target.value })}
          />
          
          <h5>📦 Items</h5>
          {invoiceData.items.map((item, idx) => (
            <div key={idx} className="invoice-item">
              <input
                type="text"
                placeholder="Description"
                value={item.description}
                onChange={(e) => {
                  const newItems = [...invoiceData.items];
                  newItems[idx].description = e.target.value;
                  setInvoiceData({ ...invoiceData, items: newItems });
                }}
              />
              <input
                type="number"
                placeholder="Quantity"
                value={item.quantity}
                onChange={(e) => {
                  const newItems = [...invoiceData.items];
                  newItems[idx].quantity = parseInt(e.target.value) || 0;
                  setInvoiceData({ ...invoiceData, items: newItems });
                }}
              />
              <input
                type="number"
                placeholder="Unit Price"
                value={item.unit_price}
                onChange={(e) => {
                  const newItems = [...invoiceData.items];
                  newItems[idx].unit_price = parseFloat(e.target.value) || 0;
                  setInvoiceData({ ...invoiceData, items: newItems });
                }}
              />
            </div>
          ))}
          <button onClick={addInvoiceItem}>+ Add Item</button>
          
          <button 
            className="create-btn" 
            onClick={handleCreateInvoice} 
            disabled={loading === 'invoice'}
          >
            {loading === 'invoice' ? 'Creating...' : '🧾 Create Invoice'}
          </button>
        </div>
      </div>
      
      {/* Budget Builder */}
      <div className="office-section">
        <h4>📊 Create Budget</h4>
        <div className="office-form">
          <input
            type="text"
            placeholder="Budget Name (e.g., Q1 2024)"
            value={budgetData.name}
            onChange={(e) => setBudgetData({ ...budgetData, name: e.target.value })}
          />
          
          <h5>📂 Categories</h5>
          {budgetData.categories.map((cat, idx) => (
            <div key={idx} className="budget-category">
              <input
                type="text"
                placeholder="Category Name"
                value={cat.name}
                onChange={(e) => {
                  const newCats = [...budgetData.categories];
                  newCats[idx].name = e.target.value;
                  setBudgetData({ ...budgetData, categories: newCats });
                }}
              />
              <input
                type="number"
                placeholder="Budgeted Amount"
                value={cat.budgeted}
                onChange={(e) => {
                  const newCats = [...budgetData.categories];
                  newCats[idx].budgeted = parseFloat(e.target.value) || 0;
                  setBudgetData({ ...budgetData, categories: newCats });
                }}
              />
              <input
                type="number"
                placeholder="Actual Amount"
                value={cat.actual}
                onChange={(e) => {
                  const newCats = [...budgetData.categories];
                  newCats[idx].actual = parseFloat(e.target.value) || 0;
                  setBudgetData({ ...budgetData, categories: newCats });
                }}
              />
            </div>
          ))}
          <button onClick={addBudgetCategory}>+ Add Category</button>
          
          <button 
            className="create-btn" 
            onClick={handleCreateBudget} 
            disabled={loading === 'budget'}
          >
            {loading === 'budget' ? 'Creating...' : '📊 Create Budget'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default OfficeTools;