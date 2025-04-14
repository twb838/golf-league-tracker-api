def calculate_match_points(match, scores):
    results = {
        'match_id': match.id,
        'team1_points': 0,
        'team2_points': 0,
        'hole_results': []
    }
    
    for hole_number in range(1, match.league.course.holes.count() + 1):
        hole_result = calculate_hole_points(
            match.team1_id,
            match.team2_id,
            scores,
            hole_number
        )
        results['hole_results'].append(hole_result)
        results['team1_points'] += hole_result['points_team1']
        results['team2_points'] += hole_result['points_team2']
    
    return results

def calculate_hole_points(team1_id, team2_id, scores, hole_number):
    team1_scores = [s for s in scores if s.team_id == team1_id]
    team2_scores = [s for s in scores if s.team_id == team2_id]
    
    team1_best = min(ps.hole_scores[hole_number-1].strokes for ps in team1_scores)
    team2_best = min(ps.hole_scores[hole_number-1].strokes for ps in team2_scores)
    
    team1_total = sum(ps.hole_scores[hole_number-1].strokes for ps in team1_scores)
    team2_total = sum(ps.hole_scores[hole_number-1].strokes for ps in team2_scores)
    
    points_team1 = 0
    points_team2 = 0
    
    # Point for best individual score
    if team1_best < team2_best:
        points_team1 += 1
    elif team2_best < team1_best:
        points_team2 += 1
    
    # Point for team total
    if team1_total < team2_total:
        points_team1 += 1
    elif team2_total < team1_total:
        points_team2 += 1
    
    return {
        'hole_number': hole_number,
        'team1_best_player_score': team1_best,
        'team2_best_player_score': team2_best,
        'team1_total_score': team1_total,
        'team2_total_score': team2_total,
        'points_team1': points_team1,
        'points_team2': points_team2
    }