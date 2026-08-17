import React, { useState } from 'react';
import { Sparkles, AlertCircle, ArrowRight, ShieldAlert } from 'lucide-react';
import { useMultiverse } from '../../context/MultiverseContext';

const DEFAULT_FALLBACK_CHOICES = [
  {
    id: 'choice_a',
    choice_label: 'Break the firewall and escape into the Quantum Frontier',
    choice_description: 'Sever all biometric ties to the city authorities and jump through the reality breach.',
    risk_level: 'high',
    philosophical_vector: 'Defiance',
    expected_resonance: 'High',
    expected_divergence: 'Extreme'
  },
  {
    id: 'choice_b',
    choice_label: 'Form a clandestine alliance with the Memory Weavers',
    choice_description: 'Stay embedded in the subterranean district and orchestrate a quiet consciousness revolution.',
    risk_level: 'moderate',
    philosophical_vector: 'Harmony',
    expected_resonance: 'Very High',
    expected_divergence: 'Moderate'
  },
  {
    id: 'choice_c',
    choice_label: 'Surrender the shard to the Syndicate in exchange for amnesty',
    choice_description: 'Trade historical truth for personal comfort and elite status.',
    risk_level: 'low',
    philosophical_vector: 'Submission',
    expected_resonance: 'Low',
    expected_divergence: 'Low'
  }
];

export default function ChoiceCards({ choices = [] }) {
  const { executeChoice, isLoading } = useMultiverse();
  const [selectedChoiceId, setSelectedChoiceId] = useState(null);

  const displayChoices = choices && choices.length > 0 ? choices : DEFAULT_FALLBACK_CHOICES;

  const handleChoiceClick = async (choice) => {
    setSelectedChoiceId(choice.id);
    await executeChoice(choice);
    setSelectedChoiceId(null);
  };

  const getRiskColor = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'existential':
      case 'high':
        return 'var(--entropy-crimson)';
      case 'moderate':
        return 'var(--starlight-gold)';
      default:
        return 'var(--temporal-cyan)';
    }
  };

  return (
    <div style={{ marginTop: '2.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.2rem' }}>
        <Sparkles size={16} color="var(--starlight-gold)" />
        <h3
          style={{
            fontSize: '0.95rem',
            letterSpacing: '0.14em',
            textTransform: 'uppercase',
            color: 'var(--starlight-gold)',
            margin: 0
          }}
        >
          Pivotal Crossroads — Choose Your Reality Branch
        </h3>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1.2rem'
        }}
      >
        {displayChoices.map((c) => {
          const isSelected = selectedChoiceId === c.id;
          const riskColor = getRiskColor(c.risk_level);

          return (
            <div
              key={c.id}
              onClick={() => !isLoading && handleChoiceClick(c)}
              className="glass-card"
              style={{
                borderRadius: '10px',
                padding: '1.4rem',
                cursor: isLoading ? 'wait' : 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                border: isSelected ? '1px solid var(--starlight-gold)' : '1px solid var(--border-glass)',
                boxShadow: isSelected ? '0 0 25px var(--starlight-gold-glow)' : 'none',
                position: 'relative'
              }}
            >
              <div>
                {/* Header Badge */}
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '0.8rem'
                  }}
                >
                  <span
                    style={{
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      padding: '0.2rem 0.6rem',
                      borderRadius: '4px',
                      background: 'rgba(255, 255, 255, 0.05)',
                      color: riskColor,
                      border: `1px solid ${riskColor}`
                    }}
                  >
                    {c.risk_level || 'Moderate'} Risk
                  </span>

                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    {c.philosophical_vector || 'Exploration'}
                  </span>
                </div>

                {/* Title & Description */}
                <h4
                  style={{
                    fontSize: '1.05rem',
                    fontWeight: 700,
                    color: '#fff',
                    marginBottom: '0.6rem',
                    lineHeight: 1.4
                  }}
                >
                  {c.choice_label || c.title}
                </h4>
                <p
                  style={{
                    fontSize: '0.86rem',
                    color: 'var(--text-secondary)',
                    lineHeight: 1.5,
                    fontFamily: 'var(--font-body)',
                    marginBottom: '1.2rem'
                  }}
                >
                  {c.choice_description || c.description}
                </p>
              </div>

              {/* Action Button */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  paddingTop: '0.8rem',
                  borderTop: '1px solid rgba(255, 255, 255, 0.06)'
                }}
              >
                <span style={{ fontSize: '0.75rem', color: 'var(--starlight-gold)', fontWeight: 600 }}>
                  SPAWN REALITY
                </span>
                <div
                  style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    background: 'rgba(247, 200, 115, 0.15)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    border: '1px solid var(--border-gold)'
                  }}
                >
                  <ArrowRight size={14} color="var(--starlight-gold)" />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
