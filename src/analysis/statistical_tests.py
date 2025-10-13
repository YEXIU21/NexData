"""
Advanced Statistical Tests Module
Implements hypothesis testing and A/B testing

SEPARATION OF CONCERNS: Statistical hypothesis testing only
"""

import pandas as pd
import numpy as np
from scipy import stats


class HypothesisTesting:
    """Advanced statistical hypothesis tests"""
    
    @staticmethod
    def t_test_independent(group1, group2, alpha=0.05):
        """Independent samples t-test"""
        t_stat, p_value = stats.ttest_ind(group1.dropna(), group2.dropna())
        
        result = {
            't_statistic': t_stat,
            'p_value': p_value,
            'alpha': alpha,
            'significant': p_value < alpha,
            'conclusion': f"{'Reject' if p_value < alpha else 'Fail to reject'} null hypothesis",
            'interpretation': f"Groups are {'significantly different' if p_value < alpha else 'not significantly different'} (p={p_value:.4f})"
        }
        return result
    
    @staticmethod
    def t_test_paired(before, after, alpha=0.05):
        """Paired samples t-test"""
        t_stat, p_value = stats.ttest_rel(before.dropna(), after.dropna())
        
        result = {
            't_statistic': t_stat,
            'p_value': p_value,
            'alpha': alpha,
            'significant': p_value < alpha,
            'conclusion': f"{'Reject' if p_value < alpha else 'Fail to reject'} null hypothesis",
            'interpretation': f"Change is {'significant' if p_value < alpha else 'not significant'} (p={p_value:.4f})"
        }
        return result
    
    @staticmethod
    def chi_square_test(observed, expected=None, alpha=0.05):
        """Chi-square test for independence"""
        if expected is None:
            chi2, p_value, dof, expected_freq = stats.chi2_contingency(observed)
        else:
            chi2, p_value = stats.chisquare(observed, expected)
            dof = len(observed) - 1
        
        result = {
            'chi2_statistic': chi2,
            'p_value': p_value,
            'degrees_of_freedom': dof,
            'alpha': alpha,
            'significant': p_value < alpha,
            'conclusion': f"{'Reject' if p_value < alpha else 'Fail to reject'} null hypothesis",
            'interpretation': f"Variables are {'dependent/associated' if p_value < alpha else 'independent'} (p={p_value:.4f})"
        }
        return result
    
    @staticmethod
    def anova_oneway(*groups, alpha=0.05):
        """One-way ANOVA"""
        clean_groups = [g.dropna() for g in groups]
        f_stat, p_value = stats.f_oneway(*clean_groups)
        
        result = {
            'f_statistic': f_stat,
            'p_value': p_value,
            'alpha': alpha,
            'significant': p_value < alpha,
            'conclusion': f"{'Reject' if p_value < alpha else 'Fail to reject'} null hypothesis",
            'interpretation': f"Group means are {'significantly different' if p_value < alpha else 'not significantly different'} (p={p_value:.4f})"
        }
        return result
    
    @staticmethod
    def normality_test(data, alpha=0.05):
        """Shapiro-Wilk test for normality"""
        stat, p_value = stats.shapiro(data.dropna())
        
        result = {
            'statistic': stat,
            'p_value': p_value,
            'alpha': alpha,
            'normal': p_value > alpha,
            'interpretation': f"Data is {'normally distributed' if p_value > alpha else 'not normally distributed'} (p={p_value:.4f})"
        }
        return result


class ABTesting:
    """A/B Testing for e-commerce and product experiments"""
    
    @staticmethod
    def ab_test_conversion(control_conversions, control_total, 
                           treatment_conversions, treatment_total, 
                           alpha=0.05):
        """A/B test for conversion rates"""
        
        # Calculate conversion rates
        control_rate = control_conversions / control_total
        treatment_rate = treatment_conversions / treatment_total
        
        # Calculate pooled probability
        pooled_prob = (control_conversions + treatment_conversions) / (control_total + treatment_total)
        
        # Calculate standard error
        se = np.sqrt(pooled_prob * (1 - pooled_prob) * (1/control_total + 1/treatment_total))
        
        # Calculate z-statistic
        z_stat = (treatment_rate - control_rate) / se
        
        # Calculate p-value (two-tailed)
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
        
        # Calculate lift
        lift = ((treatment_rate - control_rate) / control_rate) * 100 if control_rate > 0 else 0
        
        result = {
            'control_rate': control_rate,
            'treatment_rate': treatment_rate,
            'lift_percentage': lift,
            'z_statistic': z_stat,
            'p_value': p_value,
            'alpha': alpha,
            'significant': p_value < alpha,
            'winner': 'Treatment' if (p_value < alpha and treatment_rate > control_rate) else 
                     'Control' if (p_value < alpha and control_rate > treatment_rate) else 'No clear winner',
            'interpretation': f"Treatment {'improves' if lift > 0 else 'decreases'} conversion by {abs(lift):.2f}% " +
                            f"({'statistically significant' if p_value < alpha else 'not significant'}, p={p_value:.4f})"
        }
        return result
    
    @staticmethod
    def ab_test_continuous(control_data, treatment_data, alpha=0.05):
        """A/B test for continuous metrics (e.g., revenue, time on site)"""
        
        # Calculate means
        control_mean = control_data.mean()
        treatment_mean = treatment_data.mean()
        
        # Perform t-test
        t_stat, p_value = stats.ttest_ind(control_data.dropna(), treatment_data.dropna())
        
        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt(((len(control_data)-1) * control_data.std()**2 + 
                              (len(treatment_data)-1) * treatment_data.std()**2) / 
                             (len(control_data) + len(treatment_data) - 2))
        cohens_d = (treatment_mean - control_mean) / pooled_std if pooled_std > 0 else 0
        
        # Calculate lift
        lift = ((treatment_mean - control_mean) / control_mean) * 100 if control_mean != 0 else 0
        
        result = {
            'control_mean': control_mean,
            'treatment_mean': treatment_mean,
            'lift_percentage': lift,
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'effect_size': 'Small' if abs(cohens_d) < 0.5 else 'Medium' if abs(cohens_d) < 0.8 else 'Large',
            'alpha': alpha,
            'significant': p_value < alpha,
            'winner': 'Treatment' if (p_value < alpha and treatment_mean > control_mean) else 
                     'Control' if (p_value < alpha and control_mean > treatment_mean) else 'No clear winner',
            'interpretation': f"Treatment {'increases' if lift > 0 else 'decreases'} metric by {abs(lift):.2f}% " +
                            f"({'statistically significant' if p_value < alpha else 'not significant'}, p={p_value:.4f})"
        }
        return result
    
    @staticmethod
    def sample_size_calculator(baseline_rate, mde, alpha=0.05, power=0.8):
        """Calculate required sample size for A/B test"""
        
        # Z-scores
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        # Calculate sample size
        p1 = baseline_rate
        p2 = baseline_rate * (1 + mde)
        
        pooled_p = (p1 + p2) / 2
        
        n = ((z_alpha * np.sqrt(2 * pooled_p * (1 - pooled_p)) + 
              z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) / (p2 - p1)) ** 2
        
        return {
            'sample_size_per_group': int(np.ceil(n)),
            'total_sample_size': int(np.ceil(n * 2)),
            'baseline_rate': baseline_rate,
            'minimum_detectable_effect': mde,
            'alpha': alpha,
            'power': power
        }


class ConfidenceIntervals:
    """Calculate confidence intervals"""
    
    @staticmethod
    def mean_ci(data, confidence=0.95):
        """Confidence interval for mean"""
        data_clean = data.dropna()
        mean = data_clean.mean()
        se = stats.sem(data_clean)
        ci = stats.t.interval(confidence, len(data_clean)-1, loc=mean, scale=se)
        
        return {
            'mean': mean,
            'confidence_level': confidence,
            'lower_bound': ci[0],
            'upper_bound': ci[1],
            'margin_of_error': ci[1] - mean
        }
    
    @staticmethod
    def proportion_ci(successes, total, confidence=0.95):
        """Confidence interval for proportion"""
        proportion = successes / total
        z = stats.norm.ppf((1 + confidence) / 2)
        se = np.sqrt((proportion * (1 - proportion)) / total)
        margin = z * se
        
        return {
            'proportion': proportion,
            'confidence_level': confidence,
            'lower_bound': max(0, proportion - margin),
            'upper_bound': min(1, proportion + margin),
            'margin_of_error': margin
        }
