<response>
    <results name="$response.name" >
    <!-- returns the sequence of a source feature  -->
    #for $sequence in $response.sequence:
        <gene 
            uniqueName="$sequence.uniqueName"
            length="$sequence.length"
            start="$sequence.start"
            end="$sequence.end"
            dna="$sequence.dna"
            />
    #end for
    </results>
</response>