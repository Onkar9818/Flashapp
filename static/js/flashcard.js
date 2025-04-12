
// Flashcard study functionality
document.addEventListener('DOMContentLoaded', function() {
    const flashcard = document.getElementById('flashcard');
    
    if (flashcard) {
        flashcard.addEventListener('click', function() {
            this.classList.toggle('flipped');
        });
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        const studyContainer = document.getElementById('study-container');
        if (studyContainer && studyContainer.style.display !== 'none') {
            const nextBtn = document.getElementById('next-btn');
            const prevBtn = document.getElementById('prev-btn');
            
            if (e.key === 'ArrowRight' || e.key === ' ') {
                // Next card
                if (nextBtn) nextBtn.click();
            } else if (e.key === 'ArrowLeft') {
                // Previous card
                if (!prevBtn.disabled && prevBtn) prevBtn.click();
            } else if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
                // Flip card
                if (flashcard) flashcard.click();
            }
        }
    });
});
